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
import threading
import queue
import configparser
from util import *
from flask_cors import CORS
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from model import *
from sqlalchemy import select, join
import luadata
import re
from collections import defaultdict
from sqlalchemy.orm import joinedload
script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../../config/qaas-web.conf")
# more initializations in main()
db = SQLAlchemy()
app = Flask(__name__)
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_path)
app.config['SQLALCHEMY_DATABASE_URI'] = config['web']['SQLALCHEMY_DATABASE_URI_LORE']
print(config['web']['SQLALCHEMY_DATABASE_URI_LORE'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

#can move to startup script
# See: https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/
def create_app(config):
    #config app, connect to database and get all tables in database
    CORS(app)
    
    # db = SQLAlchemy(app)

    with app.app_context():
        global conn
        conn = db.engine.connect().connection
        # conn = db.engine.connect().connection
        db_name = os.path.basename(config['web']['SQLALCHEMY_DATABASE_URI_LORE'])
    #create all tables in the model
    ########################### http request ################################
  
    @app.route('/get_application_table_info_lore', methods=['POST'])
    def get_application_table_info_lore():
        request_data = request.get_json()
        data = []
        filters = request_data.get('filters', []) 
        applications = db.session.query(Application).all()

        for application in applications:
            executions = db.session.query(Execution).filter_by(application=application).all()
            application_data = {
             'program': application.program,
             'version': application.version,
             'workload': application.workload,
             'commit_id': application.commit_id,
             'n_loops': len(executions),
             'application_id': application.table_id
            }
            data.append(application_data)
        return jsonify(
                    data=data,
                    )
    
    @app.route('/get_application_subtable_info_lore', methods=['POST'])
    def get_application_subtable_info_lore():
        request_data = request.get_json()
        data = {}
        application_id = request_data.get('application_id', []) 
        executions = db.session.query(Execution).filter_by(fk_application_id = application_id)

        for execution in executions:
            src_loop = execution.src_loops[0]
            orig_src_loop = src_loop.orig_src_loop
            mutation_number = src_loop.mutation_number
            source_id = src_loop.source.table_id if not orig_src_loop else orig_src_loop.source.table_id
            orig_filename, orig_function_name, orig_line_number, _ = extract_info_from_lore_source_code_file_name(src_loop.file)
            data.setdefault(source_id, 
            {
            'n_mutations': 0, 
            'file': orig_filename,
             'function': orig_function_name,
             'line': orig_line_number,
             'mutation_numbers': [],
             'source_id': source_id
             }
             )
            #only add a new mutation 
            if mutation_number not in data[source_id]['mutation_numbers']:
                data[source_id]['n_mutations'] += 1
                data[source_id]['mutation_numbers'].append(mutation_number)

        

      
        data = list(data.values())
        return jsonify(
                    data=data,
                    )

    @app.route('/get_lore_baseline_source_code_for_specific_loop', methods=['POST'])
    def get_lore_baseline_source_code_for_specific_loop():


        data = request.get_json()

        
        target_src_loop = get_target_src_loop_from_id(int(data.get('current_src_loop_id'))  , db.session)

        orig_src_loop = target_src_loop.orig_src_loop
        orig_source_id = target_src_loop.source.table_id if not orig_src_loop else orig_src_loop.source.table_id
        source = db.session.query(Source).filter_by(table_id = orig_source_id).one()
        source_file = decompress_file(source.content).decode('utf-8')
        return json.dumps({
            'Processed baseline': source_file,
        })
    @app.route('/get_lore_mutated_source_code_for_specific_mutation', methods=['POST'])
    def get_lore_mutated_source_code_for_specific_mutation():
        data = request.get_json()

        
        current_src_loop_id = int(data.get('current_src_loop_id'))  
        mutation_number = int(data.get('mutation_number'))  
        source_id = int(data.get('source_id'))  
        #find out what is the mutation src loop that is using this source as orig source and mutaiton number
        orig_src_loops = db.session.query(SrcLoop).filter_by(fk_source_id = source_id).all()
        for orig_src_loop in orig_src_loops:
            mutated_src_loop = db.session.query(SrcLoop).filter_by(orig_src_loop = orig_src_loop, mutation_number = mutation_number).first()
            if not mutated_src_loop:
                continue
            


            source_id = mutated_src_loop.source.table_id
            source = db.session.query(Source).filter_by(table_id = source_id).one()
            source_file = decompress_file(source.content).decode('utf-8')

            return json.dumps({
                'mutation': source_file,
            })
        
        return { 'mutation': '',}

    @app.route('/get_lore_mutated_execution_cycels_for_specific_mutation', methods=['POST'])
    def get_lore_mutated_execution_cycels_for_specific_mutation():
        data = request.get_json()

        
        mutation_number = int(data.get('mutation_number'))  
        source_id = int(data.get('source_id'))

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
        source_id = data.get('source_id')
        #get orig src loop using the source
        src_loops = db.session.query(SrcLoop).filter_by(fk_source_id = source_id, mutation_number = 0).all()
        #check which mutations are using these src)loops
        mutation_dict = {}
        for orig_src_loop in src_loops:
            mutated_src_loops = db.session.query(SrcLoop).filter_by(fk_orig_src_loop_id = orig_src_loop.table_id).all()
            if not mutated_src_loops:
                continue
            
            #add orignal data to mutation_dict
            mutation_dict[0] = {
                    "mutation": 0,
                    "trans_seq": "Preproccessed baseline",
                    "interchange": "NA",
                    "tiling": "NA",
                    "distrubution": "NA",
                    "unrolling": "NA",
                    "unroll_jam": "NA",
                    }


            #found mutated loops
        
            for mutated_src_loop in mutated_src_loops:
                mutation = mutated_src_loop.mutation
                mutated_mutation_number = mutated_src_loop.mutation_number
                #get trans_seq
                mutation_elements = [
                    {"order": mutation.interchange_order, "arg": mutation.interchange_arg},
                    {"order": mutation.tiling_order, "arg": mutation.tiling_arg},
                    {"order": mutation.unrolling_order, "arg": mutation.unrolling_arg},
                    {"order": mutation.distribution_order, "arg": mutation.distribution_arg},
                    {"order": mutation.unrolljam_order, "arg": mutation.unrolljam_arg},
                ]
                sorted_elements = sorted(
                    [elem for elem in mutation_elements if elem["order"] >= 0], 
                    key=lambda x: x["order"]
                )
                trans_seq = ','.join([elem["arg"] for elem in sorted_elements if elem["arg"]])
                #put the value into dict
                if mutated_mutation_number not in mutation_dict:
                    mutation_dict[mutated_mutation_number] = {
                    "mutation": mutated_mutation_number,
                    "trans_seq": trans_seq,
                    "interchange": mutation.interchange_arg if mutation.interchange_arg else "NA",
                    "tiling": mutation.tiling_arg if mutation.tiling_arg else "NA",
                    "distrubution": mutation.distribution_arg if mutation.distribution_arg else "NA",
                    "unrolling": mutation.unrolling_arg if mutation.unrolling_arg else "NA",
                    "unroll_jam": mutation.unrolljam_arg if  mutation.unrolljam_arg else "NA",
                    }


        res = list(mutation_dict.values())
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

        
    return app



def main(config):
    
    app = create_app(config)
    app.run(debug=True,port=5002)

if __name__ == "__main__":
    
    # thread = threading.Thread(target=create_all_tables(config))
    # thread.start()
    # thread.join()
    main(config)
