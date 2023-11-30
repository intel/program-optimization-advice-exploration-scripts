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
from util import *
from flask_cors import CORS
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
config = configparser.ConfigParser()
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
        print("called api")
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
                        mutations  = get_all_mutations_from_orig_source_loop(src_loop, db.session)
                        print(len(mutations))
                        orig_filename, orig_function_name, orig_line_number, mutation_number = extract_info_from_lore_source_code_file_name(src_loop.file)

                        #don't look at same src loop with different compilers
                        run_data_key = f'{orig_filename}_{orig_function_name}_{orig_line_number}'
                        if run_data_key in run_data:
                            continue

                        #count only orig srcloops and not repetting src loops with different compilers
                        src_loop_count += 1

                        loop_data = {
                            'file': orig_filename,
                            'function': orig_function_name,
                            'line': orig_line_number,
                            'pluto': 'Yes' if get_metric_value(static_lore_loop_metrics, 'pluto') == '1' else 'No',
                            'n_mutations': len(mutations)
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

        
    return app



def main(config):
    
    app = create_app(config)
    app.run(debug=True,port=5002)

if __name__ == "__main__":
    
    # thread = threading.Thread(target=create_all_tables(config))
    # thread.start()
    # thread.join()
    main(config)
