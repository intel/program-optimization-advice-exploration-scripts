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
from ovdb import populate_database, export_data
from util import *
from flask_cors import CORS
from model import *
from sqlalchemy import select, join
import luadata
import re
from filters import FilterContext
from model_accessor import MetricGetter
from qaas_database import QaaSDatabase
from constants import EXECUTION_METRIC_TYPES
from collections import defaultdict

script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../../config/qaas-web.conf")
# more initializations in main()
db = SQLAlchemy()
app = Flask(__name__)
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_path)
app.config['SQLALCHEMY_DATABASE_URI'] = config['web']['SQLALCHEMY_DATABASE_URI_ONEVIEW']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'
db.init_app(app)
qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
frontend_html_path = os.path.join(config['web']['FRONTEND_HTML_FOLDER_OV'])
os.makedirs(frontend_html_path, exist_ok=True)
manifest_file_path = os.path.join(frontend_html_path, 'input_manifest.csv')


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
        db.Model.metadata.reflect(bind=db.engine,schema='test')
        db_name = os.path.basename(config['web']['SQLALCHEMY_DATABASE_URI_ONEVIEW'])
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

    @app.route('/filter_run_info', methods=['GET','POST'])
    def filter_run_info():
        filters = request.json.get('filters', {})
        query_filters = []

        if 'program' in filters and filters['program']:
            query_filters.append(Application.program == filters['program'])
        if 'experiment_name' in filters and filters['experiment_name']:
            query_filters.append(Application.version == filters['experiment_name'])

        if query_filters:
            programs_tuples = db.session.query(Application.program).filter(and_(*query_filters)).distinct().all()
            experiment_names_tuples = db.session.query(Application.version).filter(and_(*query_filters)).distinct().all()
        else:
            programs_tuples = db.session.query(Application.program).distinct().all()
            experiment_names_tuples = db.session.query(Application.version).distinct().all()

        programs = [item[0] for item in programs_tuples]
        experiment_names = [item[0] for item in experiment_names_tuples]
      
        return jsonify(isError= False,
                        message= "Success",
                        programs= programs,
                        experiment_names = experiment_names,
                        statusCode= 200,
                        )

    @app.route('/ov_get_all_speedup_range', methods=['GET'])
    def ov_get_all_speedup_range():

        applications = db.session.query(Application).all()

        # Create a dictionary to store the 'orig' total time and minimum total time for each program
        program_times = defaultdict(lambda: {'orig_total_time': None, 'min_total_time': float('inf'), 'min_compiler': None})

        # Calculate the 'orig' total time and minimum total time for each program
        for application in applications:
            compiler_name = parse_experiment_name(application.version)
            program_name = application.program
            for execution in application.executions:
                if compiler_name == 'orig':
                    program_times[program_name]['orig_total_time'] = execution.time
                else:
                    if execution.time < program_times[program_name]['min_total_time']:
                        program_times[program_name]['min_total_time'] = execution.time
                        program_times[program_name]['min_compiler'] = compiler_name


        # Create a dictionary to store the speedup data
        speed_up_data = defaultdict(list)

        # Calculate the speedup for each program
        for program_name, times in program_times.items():
            speedup_r = times['orig_total_time'] / times['min_total_time']
            speed_up_data[times['min_compiler']].append({'speedup_r': speedup_r})


        return speed_up_data




    @app.route('/get_application_table_info_ov', methods=['POST'])
    def get_application_table_info_ov():
        request_data = request.get_json()
        filters = filters = request_data.get('filters', []) 
        print(filters)
        filter_context = FilterContext(filters, db.session)

        data = []
        applications = db.session.query(Application).all()
        for application in applications:

            run_data = []

            for execution in filter_context.apply_all_filters(application.executions):
                if len(execution.maqaos) == 0:
                    continue  

                #TODO data needs to be read from config column
                execution_data = {
                    'timestamp': universal_timestamp_to_datetime(execution.universal_timestamp),
                    'machine': execution.os.hostname,
                    'data': '',
                    
                }
                application_data = {
                    'program': application.program,
                    'experiment_name': application.version,
                    'workload': application.workload,
                    'commit_id': application.commit_id,
                    'run_data': run_data,
                    # Start of metric collection
                }
                run_data.append(execution_data)
                
                #add all rest of interested metric types into application data
                for metric_type in EXECUTION_METRIC_TYPES:
                    value = MetricGetter(db.session, metric_type, execution).get_value()
                    application_data[metric_type] = value


                #extract flags from compilation options flags
                all_flags = application_data['compilation_flags']
                application_data['o2_o3'] = is_flag_in_compiler('O2', all_flags) or is_flag_in_compiler('O3', all_flags)
                application_data['icl_hsw'] = is_flag_in_compiler('icelake', all_flags) or is_flag_in_compiler('haswell', all_flags)
                application_data['flto'] = is_flag_in_compiler('flto', all_flags)
                application_data['fno_tree_vec'] = is_flag_in_compiler('fno-tree-vectorize', all_flags)


                if len(run_data) > 0:
                    data.append(application_data)
        return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    data=data,
                    )



    @app.route('/compute_speed_up_data_using_baseline_ov', methods=['POST'])
    def compute_speed_up_data_using_baseline_ov():
        data = request.get_json()
        selectedRows = data['selectedRows']
        baseline = data['baseline']

        speedup_graph_data = {"labels": [], "speedup": []}

        
        #get baseline total time from baseline
        baseline_total_time, baselin_execution = get_total_time_from_row(baseline)

         # Baseline has a speedup of 1
        speedup_graph_data["labels"].append(f' {parse_experiment_name(baselin_execution.application.version)}')
        speedup_graph_data["speedup"].append(1)

        #get total time from selected rows
        for row in selectedRows:
            total_time, execution = get_total_time_from_row(row)
            speed_up = float(baseline_total_time) / float(total_time) 
            speedup_graph_data["labels"].append(f' {parse_experiment_name(execution.application.version)}')
            speedup_graph_data["speedup"].append(speed_up)
        return speedup_graph_data

    def get_total_time_from_row(row):
        execution = db.session.query(Execution).filter_by(universal_timestamp = datetime_to_universal_timestamp(row['timestamp']) ).one()
        total_time = MetricGetter(db.session, "total_time", execution).get_value()
        return total_time, execution




    @app.route('/run_comparative_view_for_selected_runs', methods=['POST'])
    def run_comparative_view_for_selected_runs():
        selected_runs = request.get_json()
        data_folder_list = []
        for run in selected_runs:
            timestamp = run['timestamp']
            universal_timestamp = datetime_to_universal_timestamp(timestamp)
            print(universal_timestamp)
            export_data(universal_timestamp, qaas_output_folder, db.session)
            data_folder_list.append(qaas_output_folder)
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
dir;{run_id};env_dir;{output_data_dir}/shared/run_0;
"""
    if os.path.exists(f'{output_data_dir}/shared/run_0/decan.csv'):
        higher_level_content = f"""file;{run_id};decan;{output_data_dir}/shared/run_0/decan.csv;
        file;{run_id};vprof;{output_data_dir}/shared/run_0/vprof.csv;
        dir;{run_id};asm_mapping_dir;{output_data_dir}/tools/decan/run_{run_id}/others;"""
        content += higher_level_content

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

    manifest_file_path = os.path.join(frontend_html_path, 'input_manifest.csv')
    opt_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'], 'opt')
    orig_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'], 'orig')
    data_folder_list = [opt_folder, orig_folder]
    create_manifest_comparison(manifest_file_path, data_folder_list)
    manifest_out_path = create_out_manifest(frontend_html_path)

    run_otter_command(manifest_file_path, manifest_out_path)


  
def update_html(version):

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
