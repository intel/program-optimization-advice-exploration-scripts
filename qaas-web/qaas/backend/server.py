#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# MIT License

# Copyright (c) 2023 Intel-Sandbox
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# HISTORY
# Created October 2022
# Contributors: Yue/David
from glob import glob
import pandas
from sqlalchemy import null
from flask import Flask,Response
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from multiprocessing import Process, Queue
import pandas as pd
import subprocess
import json
import pandas as pd
import os
import time
from pathlib import Path
import shutil
from datetime import datetime
import qaas
import threading
import queue
from qaas import launch_qaas
import configparser
from ovdb import populate_database, export_data
from util import *
from flask_cors import CORS
from model import *
from sqlalchemy import select, join
import luadata
import re
from collections import defaultdict
from sqlalchemy.orm import joinedload
script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../../../config/qaas-web.conf")
# more initializations in main()
db = SQLAlchemy()
app = Flask(__name__)
config = configparser.ConfigParser()
config.read(config_path)
app.config['SQLALCHEMY_DATABASE_URI'] = config['web']['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'
db.init_app(app)
qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
frontend_html_path = os.path.join(config['web']['FRONTEND_HTML_FOLDER_OV'])
os.makedirs(frontend_html_path, exist_ok=True)
manifest_file_path = os.path.join(frontend_html_path, 'input_manifest.csv')

class QaaSThread(threading.Thread):
    def __init__(self, json_file, qaas_data_folder, qaas_message_queue):
        super().__init__()
        self.json_file = json_file
        self.qaas_data_folder = qaas_data_folder
        self.qaas_message_queue = qaas_message_queue


    def run(self):
        self.rc, self.output_ov_dir = launch_qaas (self.json_file, lambda msg: self.qaas_message_queue.put(msg), self.qaas_data_folder)


#can move to startup script
# See: https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/
def create_app(config):
    #config app, connect to database and get all tables in database

    qaas_message_queue = queue.Queue()
    CORS(app)
    
    # db = SQLAlchemy(app)

    with app.app_context():
        global conn
        conn = db.engine.connect().connection
        # conn = db.engine.connect().connection
        db_name = os.path.basename(config['web']['SQLALCHEMY_DATABASE_URI'])
    #create all tables in the model
    ########################### http request ################################
    @app.route('/get_all_timestamps', methods=['GET','POST'])
    def get_all_timestamps():
        get_timestamp_table = db.metadata.tables[f'{db_name}.execution']
        query = db.session.query(get_timestamp_table.c.qaas_timestamp.distinct())
        timestamps = pd.read_sql_query(query.statement, query.session.bind).values
        time_list = [timestamp[0] for timestamp in timestamps]
        time_list = json.dumps(time_list)
        return jsonify(isError= False,
                        message= "Success",
                        timestamps= time_list,
                        statusCode= 200,
                        )
    
    @app.route('/get_qaas_compiler_comparison_historgram_data', methods=['GET'])
    def get_qaas_compiler_comparison_historgram_data():
        df = pd.read_excel('/nfs/site/proj/alac/members/yue/mock_QaaS_Min_Max_Unicore_Perf_Default.xlsx', header=3)
        
        # List to store unique compilers
        compilers = ['ICX', 'ICC', 'GCC']

        applications = []
        delta = 0.03  # 3% threshold

        for index, row in df.iterrows():
            app_name = row['Unnamed: 0']
            icx_speedup = row['ICX: -O3 -march=native']
            icc_speedup = row['ICC: -O3 -march=native']
            gcc_speedup = row['GCC: -O3 -march=native']

            speedups = {'ICX': icx_speedup, 'ICC': icc_speedup, 'GCC': gcc_speedup}
            best_compiler = row['Best compiler'].upper()

            #  maxc(WC/c) for all compilers
            max_speedup = max([icx_speedup, icc_speedup, gcc_speedup])
            is_n_way_tie = max_speedup < (1 + delta) 

            print(app_name, best_compiler, max_speedup, is_n_way_tie)
            # Remove the best compiler from the dict
            del speedups[best_compiler]

            # Rank the other compilers
            ranked_compilers = sorted(speedups, key=speedups.get, reverse=True)

            applications.append({
                'application': app_name,
                'best_compiler': best_compiler,
                'losers': [{'compiler': loser, 'speedup': speedups[loser]} for loser in ranked_compilers],
                'is_n_way_tie': is_n_way_tie

            })

        print(applications)
        return jsonify({
            'compilers': compilers,
            'applications': applications
        })
    




    @app.route('/stream')
    def stream():

        def get_data():

            while True:
                #gotcha
                msg = qaas_message_queue.get()
                print(msg.str())
                time.sleep(1) 
                if msg.is_end_qaas():
                    break
                yield f'event: ping\ndata: {msg.str()} \n\n'

        return Response(get_data(), mimetype='text/event-stream')

    @app.route('/get_application_table_info_ov', methods=['GET'])
    def get_application_table_info_ov():
        data = []
        applications = db.session.query(Application).all()
        for application in applications:
            skip_application = False

            run_data = []
            for execution in application.executions:
                if len(execution.maqaos) == 0:
                    skip_application = True
                    break  

                #TODO data needs to be read from config column
                execution_data = {
                    'timestamp': universal_timestamp_to_datetime(execution.universal_timestamp),
                    'machine': execution.os.hostname,
                    'data': ''
                }
                run_data.append(execution_data)
            if skip_application:
                continue

            application_data = {
             'program': application.program,
             'version': application.version,
             'workload': application.workload,
             'commit_id': application.commit_id,
             'run_data': run_data

            }
            data.append(application_data)
        return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    data=data,
                    )
    @app.route('/get_application_table_info_lore', methods=['POST'])
    def get_application_table_info_lore():
        request_data = request.get_json()
        data = []
        filters = request_data.get('filters', []) 
        limit = 2000  # default page size
        #server side pagniation
        page = request_data.get('page', 0)  # default to page 0 if not provided
        pageSize = request_data.get('pageSize', 10)  # default to 10 items per page if not provided
        offset = page * pageSize


        # applications = db.session.query(Application).offset(offset).limit(pageSize).all()
        applications = db.session.query(Application).all()

        for application in applications:
            skip_application = False

            run_data = {}

            executions = db.session.query(Execution).filter_by(application=application).all()
            src_loop_count = 0
            for execution in executions:
                #check if it is lore or maqao data
                if len(execution.maqaos) != 0:
                    skip_application = True
                    break  
       
                #apply fiters
                if len(filters) > 0:
                    if not check_filters(db.session, execution, filters):
                        continue  
                

                src_loops = execution.src_loops
                for src_loop in src_loops:
                    #only look at the original source loop, i.e mutation number = 0
                    if src_loop.mutation_number != 0:
                        continue

                    

                    
                  

                    if src_loop.loops:
                        static_lore_loop_metrics = src_loop.source.source_metrics
                        orig_filename, orig_function_name, orig_line_number, mutation_number = extract_info_from_lore_source_code_file_name(src_loop.file)

                        #don't look at same src loop with different compilers
                        run_data_key = f'{orig_filename}_{orig_function_name}_{orig_line_number}'
                        if run_data_key in run_data:
                            continue

                        #count only orig srcloops and not repetting src loops with different compilers
                        src_loop_count += 1

                        n_mutations = count_mutations_for_orig_src_loop(db.session, orig_filename, orig_function_name, orig_line_number)

                        loop_data = {
                            'file': orig_filename,
                            'function': orig_function_name,
                            'line': orig_line_number,
                            'pluto': 'Yes' if get_metric_value(static_lore_loop_metrics, 'pluto') == '1' else 'No',
                            'n_mutations': n_mutations
                        }
                        run_data[run_data_key] = loop_data

            if skip_application:
                continue
            
            application_data = {
             'program': application.program,
             'version': application.version,
             'workload': application.workload,
             'commit_id': application.commit_id,
             'n_loops': src_loop_count,
             'run_data': list(run_data.values())

            }
            if len(run_data) > 0:
                data.append(application_data)

        total_count = db.session.query(Application).count()
        return jsonify(
                    totalCount= total_count,
                    data=data,
                    )

    @app.route('/get_lore_baseline_source_code_for_specific_loop', methods=['POST'])
    def get_lore_baseline_source_code_for_specific_loop():


        data = request.get_json()

        
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)

        orig_filename, orig_function_name, orig_line_number, mutation_number = extract_info_from_lore_source_code_file_name(target_src_loop.file)


        workload = target_src_loop.execution.application.workload
        program = target_src_loop.execution.application.program
        workload_version = target_src_loop.execution.application.version

        source_dir = os.path.join(config['web']['LORE_SOURCE_DIR'], workload, workload_version, program, 'extractedLoops')
      
        orig_src_file_path = os.path.join(source_dir, f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c')
        processed_src_file_path = os.path.join(source_dir, f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c.preproc.c')
        with open(orig_src_file_path, 'r') as f:
            orig_code = f.read()

        with open(processed_src_file_path, 'r') as f:
            processed_code = f.read()
        return {
            'Original baseline': orig_code,
            'Processed baseline': processed_code
        }
    @app.route('/get_lore_mutated_source_code_for_specific_mutation', methods=['POST'])
    def get_lore_mutated_source_code_for_specific_mutation():
        data = request.get_json()

        
        current_src_loop_id = int(data.get('current_src_loop_id'))  
        mutation_number = int(data.get('mutation_number'))  
        target_src_loop = db.session.query(SrcLoop).filter_by(table_id = current_src_loop_id).one()

        orig_filename, orig_function_name, orig_line_number, mutation_number = extract_info_from_lore_source_code_file_name(target_src_loop.file)


        workload = target_src_loop.execution.application.workload
        program = target_src_loop.execution.application.program
        workload_version = target_src_loop.execution.application.version

        source_dir = os.path.join(config['web']['LORE_SOURCE_DIR'], workload, workload_version, program, 'extractedLoops')
        mutated_code_path = os.path.join(source_dir, f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c_mutations', f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c.{target_src_loop.mutation_number}.c')
        with open(mutated_code_path, 'r') as f:
            orig_code = f.read()
        return {
            'mutation': orig_code
        }

    @app.route('/get_lore_mutated_execution_cycels_for_specific_mutation', methods=['POST'])
    def get_lore_mutated_execution_cycels_for_specific_mutation():
        data = request.get_json()

        
        mutation_number = int(data.get('mutation_number'))  
        #orig src loop
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)

        base_ref = int(data.get('base_ref'))  
        min_base_ref = int(data.get('min_base_ref'))  

        orig_filename, orig_function_name, orig_line_number, _ = extract_info_from_lore_source_code_file_name(target_src_loop.file)

        file_pattern = f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c.%'
        src_loops = db.session.query(SrcLoop).filter(SrcLoop.file.like(file_pattern), SrcLoop.mutation_number == mutation_number).all()
        performance_data = {}

        for src_loop in src_loops:
            for loop in src_loop.loops:
                current_compiler = loop.compiler
                vendor = current_compiler.vendor
                version = current_compiler.version
                cpu = src_loop.execution.hwsystem.hw_name
                all_values = get_metrics_for_loop(loop)
               
                vendor_version_cpu_key = f"{vendor} {version} {cpu}"

            #extra string values
            all_values['compiler'] = vendor
            all_values['version'] = version
            all_values['cpu'] = cpu
            all_values['mutation'] = src_loop.mutation_number
            all_values['base_ref'] = base_ref 
            all_values['min_base_ref'] = min_base_ref 

            performance_data[vendor_version_cpu_key] = all_values
        return jsonify(performance_data)

    @app.route('/get_lore_dynamic_metrics_for_specific_mutation', methods=['POST'])
    def get_lore_dynamic_metrics_for_specific_mutation():
        data = request.get_json()

        
        #orig src loop
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)

        #from orig loop get mutation src loop
        mutated_src_loop = get_mutated_src_loop_from_orig_src_loop(int(data.get('current_mutation_number')), target_src_loop, db.session)

        current_metrics = mutated_src_loop.loops[0].lore_loop_measures[0].lore_loop_measure_metrics
        hardware_dynamic_metrics, derived_metrics, dynamic_instr_cnts = classify_metrics(current_metrics)
        return {
            'hardware_dynamic_metrics': hardware_dynamic_metrics,
            'derived_metrics' : derived_metrics,
            'dynamic_instr_cnts' : dynamic_instr_cnts
        }


    @app.route('/get_lore_speedups_for_specific_mutation', methods=['POST'])
    def get_lore_speedups_for_specific_mutation():
        data = request.get_json()
  
        vendor_data = data.get('vendor_data')

        # Extract relevant values from data
        base_ref = float(vendor_data.get('base_ref'))
        min_base_ref = float(vendor_data.get('min_base_ref'))
        flags = ['avx', 'avx2', 'sse', 'novec', 'base']

        min_vendor_value = min([float(vendor_data[flag]) for flag in flags])

        speedup_r = [base_ref / float(vendor_data[flag]) for flag in flags]
        speedup_m = [min_base_ref / min_vendor_value for flag in flags]
        

        return jsonify({
            'speedup_r': speedup_r,
            'speedup_m': speedup_m
        })



    @app.route('/get_lore_cpu_info_for_specific_loop', methods=['POST'])
    def get_lore_cpu_info_for_specific_loop():
        data = request.get_json()
        
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)

        execution = target_src_loop.execution
        os_info = execution.os.hostname
        hw_name = execution.hwsystem.hw_name
        cpu = execution.hwsystem.cpui_model_name
        memory = execution.hwsystem.memory
        return [f'{cpu} {hw_name} {memory} {os_info}']

    @app.route('/get_mutation_data_for_specific_loop', methods=['POST'])
    def get_mutation_data_for_specific_loop():
        # Get the parameters from the request
        data = request.get_json()
        
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)

        orig_filename, orig_function_name, orig_line_number, mutation_number = extract_info_from_lore_source_code_file_name(target_src_loop.file)

        file_pattern = f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c.%'
        src_loops = db.session.query(
                SrcLoop.mutation_number, 
                Mutation.interchange_arg, 
                Mutation.tiling_arg, 
                Mutation.distribution_arg, 
                Mutation.unrolling_arg, 
                Mutation.unrolljam_arg,
                func.count(SrcLoop.mutation_number)
                ).join(
                    Mutation, SrcLoop.fk_mutation_id == Mutation.table_id
                ).filter(
                    SrcLoop.file.like(file_pattern)
                ).group_by(
                    SrcLoop.mutation_number,
                    Mutation.interchange_arg,
                    Mutation.tiling_arg,
                    Mutation.distribution_arg,
                    Mutation.unrolling_arg,
                    Mutation.unrolljam_arg
                ).all()

        res = []
        trans_seq_map = {
            0: 'Preprocessed baseline',
            1: 'Unrolling(factor=2)',
            2: 'Unrolling(factor=4)',
            3: 'Unrolling(factor=8)'
        }
        for mutation_number, interchange_arg, tiling_arg, distribution_arg, unrolling_arg, unroll_jam_arg, count in src_loops:
            data = {
                "mutation": mutation_number,
                "trans_seq": trans_seq_map[mutation_number],
                "interchange": interchange_arg,
                "tiling": tiling_arg,
                "distrubution": distribution_arg,
                "unrolling": unrolling_arg,
                "unroll_jam": unroll_jam_arg,
            }
            res.append(data)

        return res

    @app.route('/lore_get_all_speedup_range', methods=['GET'])
    def lore_get_all_speedup_range():
        all_speedup_data={}
        applications = db.session.query(Application).all()


        # Calculate the 'orig' total time and minimum total time for each program
        for current_application in applications:
            for execution in current_application.executions:
                for src_loop in execution.src_loops:
                    orig_filename, orig_function_name, orig_line_number, target_mutation_number = extract_info_from_lore_source_code_file_name(src_loop.file)
                    speed_up_data, current_src_loop_id = calculate_speedup_for_loop(current_application.executions, orig_filename, orig_function_name, orig_line_number)
                    all_speedup_data[current_src_loop_id] = speed_up_data


        print(all_speedup_data)
        return all_speedup_data

    


    @app.route('/get_all_speedup_data_for_specific_loop', methods=['POST'])
    def get_all_speedup_data_for_specific_loop():
        data = request.get_json()
        loop_file = data.get('file')
        loop_functionName = data.get('function')
        loop_line = int(data.get('line'))
        workload = data.get('workload')
        program = data.get('program')
        workload_version = data.get('workload_version')
        
        current_application = db.session.query(Application).filter_by(workload=workload, version=workload_version, program=program).first()

        executions = current_application.executions
        speed_up_data, current_src_loop_id = calculate_speedup_for_loop(current_application.executions, loop_file, loop_functionName, loop_line)

        return jsonify({
            'speed_up_data': speed_up_data,
            'current_src_loop_id': current_src_loop_id,
        })

  

    @app.route('/get_performance_data_for_specific_loop', methods=['POST'])
    def get_performance_data_for_specific_loop():
        # Get the parameters from the request
        data = request.get_json()
        
        
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)


        orig_filename, orig_function_name, orig_line_number, target_mutation_number = extract_info_from_lore_source_code_file_name(target_src_loop.file)

        file_pattern = f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c.%'
        src_loops = db.session.query(SrcLoop).filter(SrcLoop.file.like(file_pattern)).all()

        matched_loops_baseline = {}
        matched_loops_mutation = {}

        for src_loop in src_loops:
            loops = src_loop.loops
            current_mutation_number = src_loop.mutation_number

            for loop in loops:
                current_compiler = loop.compiler
                current_metrics = loop.lore_loop_measures[0].lore_loop_measure_metrics
                #pass the date instead month/year
                #need to 
                date = current_compiler.release_date.strftime("%d %b %Y")
                key = current_compiler.vendor
                current_value = float(get_metric_value(current_metrics, 'base_median'))
        
                if current_mutation_number == 0:
                    if key not in matched_loops_baseline:
                        matched_loops_baseline[key] = {}
                    matched_loops_baseline[key][date] = min(current_value, matched_loops_baseline[key].get(date, float('inf')))
                else:

                    other_values = [
                        float(get_metric_value(current_metrics, metric))
                        for metric in ['avx_median', 'avx2_median', 'o3_median', 'sse_median','base_median']
                    ]
                    if key not in matched_loops_mutation:
                        matched_loops_mutation[key] = {}
                    matched_loops_mutation[key][date] = min(min(other_values), matched_loops_mutation[key].get(date, float('inf')))

        # Convert the data to the desired format for output
        for key in matched_loops_baseline:
            matched_loops_baseline[key] = [{'x': date, 'y': value} for date, value in matched_loops_baseline[key].items()]
        for key in matched_loops_mutation:
            matched_loops_mutation[key] = [{'x': date, 'y': value} for date, value in matched_loops_mutation[key].items()]

        return jsonify({
            'baseline': matched_loops_baseline,
            'mutation': matched_loops_mutation,
        })
    
    @app.route('/get_lore_static_loop_info_for_specific_loop', methods=['POST'])
    def get_lore_static_loop_info_for_specific_loop():
        data = request.get_json()
        
        
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)


        loop_static_metrics = target_src_loop.source.source_metrics
        res = [
            { 'column': 'Nest levels', 'value': get_metric_value(loop_static_metrics, 'nest_level') },
            { 'column': 'Statements', 'value': get_metric_value(loop_static_metrics, 'mem_access_cnt') },
            { 'column': 'Memory accesses', 'value': get_metric_value(loop_static_metrics, 'mem_access_cnt') },
            { 'column': 'Floating point binary operations', 'value': get_metric_value(loop_static_metrics, 'fp_bin_op_cnt') },
            { 'column': 'Integer binary operations', 'value': get_metric_value(loop_static_metrics, 'int_bin_op_cnt') },
            { 'column': 'Integer unary operations', 'value': get_metric_value(loop_static_metrics, 'int_un_op_cnt') },
            { 'column': 'Assignments', 'value': get_metric_value(loop_static_metrics, 'assign_cnt') },
            { 'column': 'Constants', 'value': get_metric_value(loop_static_metrics, 'const_cnt') },
            { 'column': 'Constant 0s', 'value': get_metric_value(loop_static_metrics, 'const_0_cnt') },
            { 'column': 'Constant 1s', 'value': get_metric_value(loop_static_metrics, 'const_1_cnt') },
            { 'column': 'Binary operations with integer constants', 'value': get_metric_value(loop_static_metrics, 'bin_op_with_int_const_cnt') },
            { 'column': 'Basic blocks', 'value': get_metric_value(loop_static_metrics, 'bb_cnt') },
            { 'column': 'Basic blocks with 1 successor', 'value': get_metric_value(loop_static_metrics, 'bb_1_succ_cnt') },
            { 'column': 'Basic blocks with 2 successors', 'value': get_metric_value(loop_static_metrics, 'bb_2_succ_cnt') },
            { 'column': 'Basic blocks with 3 or more successors', 'value': get_metric_value(loop_static_metrics, 'bb_3_plus_succ_cnt') },
            { 'column': 'Basic blocks with 1 predecessor', 'value': get_metric_value(loop_static_metrics, 'bb_1_pred_cnt') },
            { 'column': 'Basic blocks with 2 predecessors', 'value': get_metric_value(loop_static_metrics, 'bb_2_pred_cnt') },
            { 'column': 'Basic blocks with 3 or more predecessors', 'value': get_metric_value(loop_static_metrics, 'bb_3_plus_pred_cnt') },
            { 'column': 'Basic blocks with 1 predecessor and 1 successor', 'value': get_metric_value(loop_static_metrics, 'bb_1_pred_1_succ_cnt') },
            { 'column': 'Basic blocks with 1 predecessor and 2 successors', 'value': get_metric_value(loop_static_metrics, 'bb_1_pred_2_succ_cnt') },
            { 'column': 'Basic blocks with 2 predecessors and 1 successor', 'value': get_metric_value(loop_static_metrics, 'bb_2_pred_1_succ_cnt') },
            { 'column': 'Basic blocks with 2 predecessors and 2 successors', 'value': get_metric_value(loop_static_metrics, 'bb_2_pred_2_succ_cnt') },
            { 'column': 'Basic blocks with 3 or more predecessors and 3 or more successors', 'value': get_metric_value(loop_static_metrics, 'bb_3_plus_pred_3_plus_succ_cnt') },
            { 'column': 'Basic blocks with 1 to 5 statements', 'value': get_metric_value(loop_static_metrics, 'bb_5_minus_stmt_cnt') },
            { 'column': 'Basic blocks with 6 to 10 statements', 'value': get_metric_value(loop_static_metrics, 'bb_6_to_10_stmt_cnt') },
            { 'column': 'Basic blocks with 11 or more statements', 'value': get_metric_value(loop_static_metrics, 'bb_11_plus_stmt_cnt') },
            { 'column': 'Control flow graph edges', 'value': get_metric_value(loop_static_metrics, 'cfg_edge_cnt') },
            { 'column': 'Whether contain branches', 'value': get_metric_value(loop_static_metrics, 'has_branch') },         
        ]

        
        return res

    @app.route('/run_comparative_view_for_selected_runs', methods=['POST'])
    def run_comparative_view_for_selected_runs():
        selected_runs = request.get_json()
        data_folder_list = []
        for run in selected_runs:
            print(run)
            timestamp = run['timestamp']
            universal_timestamp = datetime_to_universal_timestamp(timestamp)
            print(universal_timestamp)
            output_folder = os.path.join(qaas_output_folder, universal_timestamp)
            export_data(universal_timestamp, output_folder, db.session)
            data_folder_list.append(output_folder)
        create_manifest_comparison(manifest_file_path, data_folder_list)
        manifest_out_path = create_out_manifest(frontend_html_path)

        run_otter_command(manifest_file_path, manifest_out_path)
        return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    )
    @app.route('/create_new_timestamp', methods=['GET','POST'])
    def create_new_timestamp():
        
        #real user input data  unused for now
        qaas_request = request.get_json()
        
        #call backplane and wait to finish
        json_file = config['web']['INPUT_JSON_FILE']
        # t = QaaSThread(json_file, config['web']['QAAS_DATA_FOLDER'], qaas_message_queue)
        # t.start()
        # t.join()
        
        # output_ov_dir = t.output_ov_dir
        # output_ov_dir = "/nfs/site/proj/alac/tmp/qaas-fix/tmp/qaas_data/167-50-406"
        output_ov_dir = "/nfs/site/proj/alac/tmp/qaas-fix/tmp/qaas_data/167-80-123"

        ov_output_dir = os.path.join(output_ov_dir,'oneview_runs')
        for version in ['opt','orig']:
            ov_version_output_dir = os.path.join(ov_output_dir, version)
            result_folders = os.listdir(ov_version_output_dir)
            # Should have only one folder
            assert len(result_folders) == 1
            result_folder = result_folders[0]
            current_ov_dir = os.path.join(ov_version_output_dir, result_folder)
            qaas_timestamp = os.path.basename(output_ov_dir)
            workload_name = f"workload_name_{version}"
            workload_version_name = f"version_name({version})"
            workload_program_name = f"test_program_name_{version}"
            workload_program_commit_id = f"test###id_{version}"
            populate_database(current_ov_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
            update_html(version)
        
        #if True:
        run_comparison_report()

        return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    timestamp=qaas_timestamp,
                    )


    @app.route('/get_html_by_timestamp', methods=['GET','POST'])
    def get_html_by_timestamp():
        #place to put files
        query_time = request.get_json()['timestamp'] 
        query_time = datetime_to_universal_timestamp(query_time)

        export_data(query_time, qaas_output_folder, db.session)
        
        create_manifest_monorun(manifest_file_path,qaas_output_folder)
        manifest_out_path = create_out_manifest(frontend_html_path)

        run_otter_command(manifest_file_path, manifest_out_path)
        # print(query_time)
        # for version in ['opt','orig']:
        #     update_html(version)
        # run_comparison_report()

        #get table using timestamp
        return jsonify(isError= False,
                        message= "Success",
                        statusCode= 200,
                        )



    @app.route('/get_data_table_rows', methods=['GET','POST'])
    def get_data_table_rows():
        #get application, machine, and dataset
        #dataset and application in config.lua
        #machine in local_var
        #get all timestamps, for each time stamp, get machine
        local_vars = db.metadata.tables[f'{db_name}.execution']
        query = db.session.query(local_vars.c.qaas_timestamp.distinct())
        timestamps = pd.read_sql_query(query.statement, query.session.bind).values
        #TODO get all machine instead of just 1
        perm_path = os.path.join(config['web']['PERM_DATA_FOLDER'],timestamps[0][0], 'orig')

        machine_query = db.session.query(local_vars.c.hostname.distinct())
        machines = pd.read_sql_query(machine_query.statement, query.session.bind).values

        machine =  machines[0][0] if len(machines) == 1 else ''
        config_path = f"{perm_path}/shared/run_0/config.lua"
        config_file = open(config_path, 'r')
        lines = config_file.readlines()
        application = str(lines[0].split("=")[1][2:-2])
        dataset = str(lines[1].split("=")[1][:-4])
        data={"Application":application, "Machine":machine, "Dataset":dataset}

        return jsonify(isError= False,
                        data= json.dumps(data),
                        message= "Success",
                        statusCode= 200,
                        )
        
        
    return app

def delete_created_path(path_list):
    for path in path_list:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def run_otter_command(manifest_file_path, out_manifest_path):
    cdcommand= f"cd {os.path.dirname(manifest_file_path)};"
    ottercommand = f"{config['web']['MAQAO_VERSION']} otter --input={manifest_file_path} --output={out_manifest_path}"  
    command = cdcommand +  ottercommand
    print(ottercommand)
    ret = subprocess.run(command, capture_output=True, shell=True)
    print(ret.stdout.decode())
   

def create_manifest_file_for_run(run_id, run_name, output_data_dir, manifest_path):
    content =  f"""meta;{run_id};{run_name};run_{run_id};
virtual;0;executable;./mpi_hello_world;
file;{run_id};expert_run;{output_data_dir}/shared/run_0/expert_run.csv;
file;{run_id};config;{output_data_dir}/shared/run_0/config.lua;
file;{run_id};localvars;{output_data_dir}/shared/run_0/local_vars.csv;
dir;{run_id};lprof_dir;{output_data_dir}/shared/lprof_npsu_run_0;
dir;{run_id};cqa_dir;{output_data_dir}/static_data/cqa;
dir;{run_id};sources_dir;{output_data_dir}/static_data/sources;
dir;{run_id};asm_dir;{output_data_dir}/static_data/asm;
dir;{run_id};groups_dir;{output_data_dir}/static_data/groups;
dir;{run_id};hierarchy_dir;{output_data_dir}/static_data/hierarchy;
file;{run_id};global_metrics;{output_data_dir}/shared/run_0/global_metrics.csv;
file;{run_id};categorization;{output_data_dir}/shared/run_0/lprof_categorization.csv;
dir;{run_id};callchains_dir;{output_data_dir}/shared/lprof_npsu_run_0/callchains;
file;{run_id};log;{output_data_dir}/logs/log.txt;
file;{run_id};logs_subdir;{output_data_dir}/logs/run_0;
dir;{run_id};env_dir;{output_data_dir}/shared/run_0;"""
    write_string_to_file(manifest_path, content)

def write_string_to_file(file_path, string):
    with open(file_path, 'a') as file:
        file.write(f'{string}\n')

def write_manifest_header(manifest_path, run_type):
    header=f"""type;run;usage;path;
meta;;report_type;{run_type};"""
    write_string_to_file(manifest_path, header)

def create_out_manifest(output_file_path):
    usage = 'html_dir'
    output_dir_path = os.path.join(output_file_path, 'output_html')
    data = {'usage': [usage], 'value': [output_dir_path]}
    df = pd.DataFrame(data)
    os.makedirs(output_file_path, exist_ok=True)
    out_manifest_path = os.path.join(output_file_path, 'out_manifest.csv')
    df.to_csv(out_manifest_path, index=False)
    return out_manifest_path

def create_manifest_comparison(manifest_path, output_data_dir_list):
    if os.path.isfile(manifest_path):
        os.remove(manifest_path)
    write_manifest_header(manifest_path, 'multirun')
    index = 0
    for output_data_dir in output_data_dir_list:
        create_manifest_file_for_run(index, f'run_{index}', output_data_dir, manifest_path)
        index += 1
def create_manifest_monorun(manifest_path, output_data_dir):
    if os.path.isfile(manifest_path):
        os.remove(manifest_path)
    write_manifest_header(manifest_path, 'monorun')
    create_manifest_file_for_run(0, 'run_0', output_data_dir, manifest_path)

def run_comparison_report():
    qaas_web_folder = os.path.join(config['web']['FRONTEND_HTML_FOLDER'], 'comparison_report')
    os.makedirs(qaas_web_folder, exist_ok=True)
    manifest_file_path = os.path.join(qaas_web_folder, 'input_manifest.csv')
    opt_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'], 'opt')
    orig_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'], 'orig')
    data_folder_list = [opt_folder, orig_folder]
    create_manifest_comparison(manifest_file_path, data_folder_list)
    manifest_out_path = create_out_manifest(qaas_web_folder)

    run_otter_command(manifest_file_path, manifest_out_path)


  
def update_html(version):
    #prepare path
    frontend_html_path = os.path.join(config['web']['FRONTEND_HTML_FOLDER'], version)
    os.makedirs(frontend_html_path, exist_ok=True)
    manifest_file_path = os.path.join(frontend_html_path, 'input_manifest.csv')
    output_data_dir = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'], version)
    #####create manifest.csv 
    create_manifest_monorun(manifest_file_path,output_data_dir)
    manifest_out_path = create_out_manifest(frontend_html_path)
    

    run_otter_command(manifest_file_path, manifest_out_path)

    # delete_created_path(to_delete)



    

def main(config):
    
    app = create_app(config)
    app.run(debug=True,port=5002)

if __name__ == "__main__":
    
    # thread = threading.Thread(target=create_all_tables(config))
    # thread.start()
    # thread.join()
    create_all_tables(config)
    print("finsihed creating all the tables")
    main(config)
