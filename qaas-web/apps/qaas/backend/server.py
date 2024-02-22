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

import pandas as pd

from flask import Flask,Response
from flask_cors import CORS
from flask import jsonify,request
import numpy as np
import configparser
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, exists, and_, cast
from sqlalchemy import func
import sys
import tempfile
#import files from common 
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from base_util import *
backplane_directory = os.path.normpath(os.path.join(current_directory, '../../../../qaas-backplane/src'))
sys.path.insert(0, backplane_directory)
deployment_directory = os.path.normpath(os.path.join(current_directory, '../../../deployment'))
sys.path.insert(0, deployment_directory)
from populate_db import read_qaas_ov
from qaas_ov_db import export_data
from model import *
import threading
from qaas import launch_qaas
import time
import queue
import json
import subprocess
# from qaas_ov_db import populate_database_qaas_ov

#set config
script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../../config/qaas-web.conf")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_path)
#set app
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = config['web']['SQLALCHEMY_DATABASE_URI_QAAS_OV']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)

class QaaSThread(threading.Thread):
    def __init__(self, json_file, qaas_data_folder, qaas_message_queue):
        super().__init__()
        self.json_file = json_file
        self.qaas_data_folder = qaas_data_folder
        self.qaas_message_queue = qaas_message_queue


    def run(self):
        self.rc, self.output_ov_dir = launch_qaas (self.json_file, lambda msg: self.qaas_message_queue.put(msg), self.qaas_data_folder)

def calculate_speedup(time_comp, baseline_compiler):
    baseline_time = time_comp.get(baseline_compiler, 0)
    if baseline_time == 0:
        return []

    win_lose_list = []
    for compiler, time in time_comp.items():
        speedup = baseline_time / time
        if speedup < 1:
            converted_speedup = 1 / speedup
            win_lose_list.append({'winner': baseline_compiler, 'loser': compiler, 'speedup': converted_speedup})
    return win_lose_list

def create_app(config):
    qaas_message_queue = queue.Queue()

    with app.app_context():
        global conn
        conn = db.engine.connect().connection

    #stream
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
    
    def get_unicore_data():
        architecture_mapping = {
            "SAPPHIRERAPIDS": "Intel SPR",
            "ICELAKE-SERVER": "Intel ICL"
        }
        

        #read all unicore runs that have turbo on
        #TODO ask what is the threshold to check if a machine has turbo on or off
        data = {}
        qaass = db.session.query(QaaS).join(QaaSRun.qaas).join(QaaSRun.execution).join(Execution.os).join(Execution.hwsystem).filter(Os.scaling_min_frequency > 3000000, Execution.config['MPI_threads'] == 1, Execution.config['OMP_threads'] == 1).distinct().all()
        for qaas in qaass:
            #execution obj that has min time across this qaas run
            min_time_execution = (db.session.query(Execution)
                    .join(QaaSRun.execution)
                    .filter(QaaSRun.qaas == qaas)
                    .order_by(Execution.time.asc())
                    .first())
            gflops = min_time_execution.global_metrics['Gflops']
            app_name = min_time_execution.application.workload
            architecture = min_time_execution.hwsystem.architecture
            architecture = architecture_mapping.get(architecture)

            if app_name not in data:
                data[app_name] = {"Apps": app_name, "Intel ICL": None, "Intel SKL": None, "Intel SPR": None, "AMD Zen4": None, "AWS G3E": None}
        
            data[app_name][architecture] = gflops

        df = pd.DataFrame(list(data.values()))

        #sort by x axis
        df['Mean'] = df.drop(columns=['Apps']).mean(axis=1)
        df.sort_values('Mean', inplace=True)
        df.drop('Mean', axis=1, inplace=True)


        

        return df

    @app.route('/get_qaas_unicore_perf_gflops_data', methods=['GET'])
    def get_qaas_unicore_perf_gflops_data():
        df = get_unicore_data()
        data_dict = df.to_dict(orient='list')
        # replace NaN with None (null in JSON)
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]
        
        return jsonify(data_dict)

    @app.route('/get_utab_data', methods=['GET'])
    def get_utab_data():
        df = get_unicore_data()
        data_dict = df.to_dict(orient='list')
        # replace NaN with None (null in JSON)
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]
        return jsonify(data_dict)

    def get_multicore_data():
        architecture_mapping = {
            "SAPPHIRERAPIDS": "SPR",
            "ICELAKE-SERVER": "ICL"
        }
        data = {}
        #get multicore qaas runs        
        qaass = db.session.query(QaaS)\
            .join(QaaSRun.qaas)\
            .join(QaaSRun.execution)\
            .join(Execution.os)\
            .join(Execution.hwsystem)\
            .filter(
                Os.scaling_min_frequency < 3000000,
                or_(
                     Execution.config['MPI_threads'] > 1,
                     Execution.config['OMP_threads'] > 1
                )
            )\
            .distinct().all()
        for qaas in qaass:
            scalability_qaas_runs = db.session.query(QaaSRun).filter_by(qaas = qaas, type = "scalability_report" ).all()
            #TODO this check is not very good
            if len(scalability_qaas_runs) == 0:
                # print("not scalability reoirt", qaas.timestamp)

                continue

            #get multicompiler run and scability run
            best_qaas_execution = db.session.query(Execution)\
                .join(QaaSRun.execution)\
                .filter(QaaSRun.qaas == qaas, QaaSRun.type == "multicompiler_report")\
                .order_by(Execution.time)\
                .first()
            best_qaas_compiler = best_qaas_execution.compiler_option.compiler.vendor
            # print(best_qaas_compiler)
            ref_qaas_run = db.session.query(QaaSRun).join(QaaSRun.execution).join(Execution.compiler_option).join(CompilerOption.compiler)\
                        .filter(QaaSRun.qaas == qaas, QaaSRun.type == "scalability_report", Compiler.vendor == best_qaas_compiler, Execution.config['MPI_threads'] == 1,  Execution.config['OMP_threads'] == 1,  Execution.time != None).first()
            #for case like https://gitlab.com/amazouz/qaas-runs/-/blob/main/runs/169-617-8814/qaas_multicore.csv?ref_type=heads just skip
            if not ref_qaas_run:
                # print("cannot find ref time", qaas.timestamp)

                continue
            
            ref_time = ref_qaas_run.execution.time
            # print(ref_qaas_run.qaas.timestamp, ref_qaas_run.execution.application.workload,  ref_qaas_run.execution.hwsystem.architecture)
            best_compiler_qaas_runs = db.session.query(QaaSRun).join(QaaSRun.execution).join(Execution.compiler_option).join(CompilerOption.compiler)\
                        .filter(QaaSRun.qaas == qaas, QaaSRun.type == "scalability_report", Compiler.vendor == best_qaas_compiler).all()
            #find max speedup and associated execution
            max_speedup = 0
            max_execution = None
            max_time = None
            for qaas_run in best_compiler_qaas_runs:
                current_execution = qaas_run.execution
                current_run_time =  current_execution.time
                num_mpi = current_execution.config['MPI_threads']
                num_omp = current_execution.config['OMP_threads']
                #get time for qaas run that has time
                if not current_run_time:
                    # print("does not have time", qaas_run.qaas.timestamp)
                    continue
                speedup_num_mpi = 1 if current_execution.application.mpi_scaling == 'strong' else num_mpi
                speedup_num_omp = 1 if current_execution.application.omp_scaling == 'strong' else num_omp

                speedup_best_compiler = (speedup_num_mpi * speedup_num_omp * ref_time) / current_run_time
                eff = speedup_best_compiler / (num_mpi * num_omp)
               
                if speedup_best_compiler > max_speedup and eff >= 0.5:
                    max_speedup = speedup_best_compiler
                    max_execution = current_execution
                    max_time = current_run_time

            # print(max_execution.time, max_speedup, max_execution.application.workload, max_execution.hwsystem.architecture)
            #fill the data
            if max_execution:
                gflops = max_execution.global_metrics['Gflops']
                cores = max_execution.config['MPI_threads'] * max_execution.config['OMP_threads']
                app_workload = max_execution.application.workload
                architecture = max_execution.hwsystem.architecture
                architecture = architecture_mapping.get(architecture)
                #check if app exist
                if app_workload not in data:
                    data[app_workload] = {"Apps": app_workload}
        
                
                # getlabels for Gflops and cores
                gf_label = f"{architecture}.Gf"
                cores_label = f"{architecture}.cores"
                time_label = f"{architecture}_time"

                # Append the data dictionary for this execution
                data[app_workload][gf_label] = gflops
                data[app_workload][cores_label] = cores
                data[app_workload][time_label] = max_execution.time
                data[app_workload]['best_compiler'] = max_execution.compiler_option.compiler.vendor.upper()


            
        df = pd.DataFrame(list(data.values()))
        # print(df)
        return df
    @app.route('/get_arccomp_data', methods=['GET'])
    def get_arccomp_data():
        df = get_multicore_data()

        #get min tiqaame from multicompiler set for applicaiton
        df['ICL per-core GFlops'] = df['ICL.Gf'] / df['ICL.cores']
        df['SPR per-core GFlops'] = df['SPR.Gf'] / df['SPR.cores']

        df['coreICL/coreSPR'] = df['ICL per-core GFlops'] / df['SPR per-core GFlops']
        df['coreSPR/coreICL'] = df['SPR per-core GFlops'] / df['ICL per-core GFlops']
        df['winner'] = np.where(df['coreICL/coreSPR'] > 1, 'ICL', 'SPR')
        df['winner ratio'] = df[['coreICL/coreSPR', 'coreSPR/coreICL']].max(axis=1)
        result_df = df[['Apps', 'winner', 'winner ratio']]
        #sort the result df
        result_df = result_df.sort_values(by='winner ratio', ascending=True)


        data_dict = result_df.to_dict(orient='list')
        # replace NaN with None (null in JSON)
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]

        return jsonify(data_dict)
    
    @app.route('/get_mpratio_data', methods=['GET'])
    def get_mpratio_data():
        df = get_multicore_data()
        ICL_CORES = 48
        SPR_CORES = 64
        df['total_cores_ratio'] = df['SPR.cores'] / df['ICL.cores']
        df.rename(columns = {'Apps':'miniapp', 'ICL.cores':'cores_icl', 'SPR.cores':'cores_spr',  'ICL.Gf':'best_total_gf'}, inplace=True)
        data_dict = df.to_dict(orient='list')
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]

        return jsonify(data_dict)

    @app.route('/get_appgain_data', methods=['GET'])
    def get_appgain_data():
        data = []
        # qaass = db.session.query(QaaS).all()
        #get icelake runs that have turbo off
        qaass = db.session.query(QaaS).join(QaaSRun.qaas).join(QaaSRun.execution).join(Execution.os).join(Execution.hwsystem).filter(Os.scaling_min_frequency < 3000000, HwSystem.architecture == "ICELAKE-SERVER").distinct().all()
        #iterate each qaas
        for qaas in qaass:
            row_data = {"min_time": None, "app_name": None}
            #get min time across compiler for same app
            min_time = db.session.query(func.min(Execution.time)).join(QaaSRun.execution).filter(QaaSRun.qaas == qaas).scalar()
            #default time
            qaas_runs = db.session.query(QaaSRun).join(QaaSRun.execution).join(Execution.compiler_option).filter(QaaSRun.qaas == qaas, CompilerOption.flag == "default" ).all()
            # print(len(qaas_runs), qaas.timestamp)
            for qaas_run in qaas_runs:
                execution = qaas_run.execution
                compiler_vendor = execution.compiler_option.compiler.vendor
                # print(compiler_vendor, qaas.timestamp, execution.application.workload)
                column_name = f"default_{compiler_vendor}_time"
                row_data[column_name] = execution.time
                if row_data["app_name"] is None:
                    row_data["app_name"] = execution.application.workload
            
            row_data["min_time"] = min_time
            data.append(row_data)
        
        df = pd.DataFrame(data).dropna()

        df['ICX: -O3 -march=native'] = df['default_icx_time'] / df['min_time']
        df['ICC: -O3 -march=native'] = df['default_icc_time'] / df['min_time']
        df['GCC: -O3 -march=native'] = df['default_gcc_time'] / df['min_time']    
        # print(df)
        df['largest_gain'] = df[['ICX: -O3 -march=native', 'ICC: -O3 -march=native', 'GCC: -O3 -march=native']].max(axis=1)
        df['app'] = df['app_name']

        result_df = df[['app', 'largest_gain']]
        result_df = result_df.sort_values(by='largest_gain', ascending=True)

        data_dict = result_df.to_dict(orient='list')
        # replace NaN with None (null in JSON)
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]
        return jsonify(data_dict)
    
    @app.route('/get_bestcomp_data', methods=['GET'])
    def get_bestcomp_data():
        multi_df = get_multicore_data()
        uni_df = get_unicore_data()

        df = pd.merge(multi_df, uni_df, on='Apps', how='inner', suffixes=('_multi_df', '_uni_df'))
        df.rename({'Apps':'miniapp', 'ICL.cores':'cores_used', 'Intel ICL':'unicore_gf', 'ICL.Gf':'gflops'}, axis=1, inplace=True)

        df['gf_per_core'] = df['gflops'] / df['cores_used']
        df['ratio_unicore_df_over_df_per_core'] = df['unicore_gf'] / df['gf_per_core']

        #add ratio
        columns_for_ratios = ['ICL_time', 'gflops', 'gf_per_core', 'unicore_gf']
        max_values = df[columns_for_ratios].max()
        min_values = df[df[columns_for_ratios] > 0][columns_for_ratios].min()
        ratios_row = {column: max_values[column] / min_values[column] if min_values[column] > 0 else None for column in columns_for_ratios}
        ratios_row['miniapp'] = 'Ratios r=max/min' 
        ratios_df = pd.DataFrame([ratios_row], columns=df.columns)
        df = pd.concat([df, ratios_df], ignore_index=True)


        data_dict = df.to_dict(orient='list')
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]

        return jsonify(data_dict)
    @app.route('/get_qaas_multicore_perf_gflops_data', methods=['GET'])
    def get_qaas_multicore_perf_gflops_data():
        df = get_multicore_data()
        #sort by x axis
        df['Mean'] = df.drop(columns=['Apps']).mean(axis=1)
        df.sort_values('Mean', inplace=True)
        df.drop('Mean', axis=1, inplace=True)
        df['ICL Gf/core'] = df['ICL.Gf'] / df['ICL.cores']
        df['SPR Gf/core'] = df['SPR.Gf'] / df['SPR.cores']
        df.drop('ICL.cores', axis=1, inplace=True)
        df.drop('SPR.cores', axis=1, inplace=True)
        df.rename({'ICL.Gf':'ICL total Gf', 'SPR.Gf':'SPR total Gf'}, axis=1, inplace=True)
        df = df.drop(columns=['ICL_time', 'best_compiler', 'SPR_time'])

        data_dict = df.to_dict(orient='list')
        # replace NaN with None (null in JSON)
        for key in data_dict.keys():
            data_dict[key] = [None if pd.isna(x) else x for x in data_dict[key]]

        return jsonify(data_dict)
    
    @app.route('/get_qaas_compiler_comparison_historgram_data', methods=['GET'])
    def get_qaas_compiler_comparison_historgram_data():
        df = pd.read_excel('/host/home/yjiao/QaaS_Min_Max_Unicore_Perf_Default.xlsx', header=3)

        # convert columns to numeric, replacing errors with NaN
        df['Best (option) perf. (s)'] = pd.to_numeric(df['Best (option) perf. (s)'], errors='coerce')
        df['ICX: -O3 -march=native'] = pd.to_numeric(df['ICX: -O3 -march=native'], errors='coerce')

  
        
        # List to store unique compilers
        compilers = ['ICX', 'ICC', 'GCC']

        applications = []
        delta = 0.03  # 3% threshold

        #get the execution time back
        df['ICX'] = df['Best (option) perf. (s)'] * df['ICX: -O3 -march=native']
        df['ICC'] = df['Best (option) perf. (s)'] * df['ICC: -O3 -march=native']
        df['GCC'] = df['Best (option) perf. (s)'] * df['GCC: -O3 -march=native']


      
        #one row is one application
        for index, row in df.iterrows():
            app_name = row['Unnamed: 0']
            if pd.isna(app_name):
                break
            icx_speedup = row['ICX: -O3 -march=native']
            icc_speedup = row['ICC: -O3 -march=native']
            gcc_speedup = row['GCC: -O3 -march=native']

            #if there is empty value just continue
            if pd.isna(icx_speedup) or pd.isna(icc_speedup) or pd.isna(gcc_speedup):
                continue
            
      
            speedups = {'ICX': icx_speedup, 'ICC': icc_speedup, 'GCC': gcc_speedup}

            best_compiler_set = sorted(set(row['Best compiler'].split("/")))
            is_n_way_tie = len(best_compiler_set) == 3

            #if it is a tie just look at next application
            if is_n_way_tie:
                applications.append({
                'application': app_name,
                'is_n_way_tie': is_n_way_tie,
                'n_way' : len(best_compiler_set),
                'win_lose': [],
                })
                continue

            best_compiler = best_compiler_set[0].upper()


            best_time_key = f'{best_compiler}qaas'
            time_comp = {'ICX': row['ICX'],'ICC': row['ICC'], 'GCC': row['GCC'], best_time_key: row['Best (option) perf. (s)']}
            all_win_lose = []

            for baseline_compiler in ['ICX', 'ICC', 'GCC', best_time_key]:
                win_lose = calculate_speedup(time_comp, baseline_compiler)
                all_win_lose.extend(win_lose)

          
            applications.append({
                'application': app_name,
                'win_lose': all_win_lose,
                'is_n_way_tie': is_n_way_tie
            })

        return jsonify({
            'compilers': compilers,
            'applications': applications
        })
    
    @app.route('/get_system_config_data', methods=['GET'])
    def get_system_config_data():
        #get all existing machines
        machines = db.session.query(HwSystem.architecture).distinct().all()
        machine_list = [tuple[0] for tuple in machines]
        data = {}
        for machine in machine_list:
            #for each machine get an execution that use the machine and get its data
            executions = db.session.query(Execution).join(Execution.hwsystem).filter(HwSystem.architecture == machine).all()
            #get an execution that is not completely emtpy
            for execution in executions:
                if execution.os.hostname:
                    hwsystem = execution.hwsystem
                    os = execution.os
                    data[machine] = {'machine': os.hostname, 'model_name': hwsystem.cpui_model_name, 'architecture': hwsystem.architecture, 'num_cores': hwsystem.cpui_cpu_cores,
                                    'freq_driver': os.driver_frequency, 'freq_governor': os.scaling_governor, 'huge_page': os.huge_pages, 'num_sockets':hwsystem.sockets, 'num_core_per_socket': hwsystem.cores_per_socket }
                    break
        
        return jsonify(data)

    @app.route('/get_job_submission_results', methods=['GET'])
    def get_job_submission_results():
        #get all qaas runs
        data = []
        qaass = db.session.query(QaaS).distinct().all()
        for qaas in qaass:
            qaas_runs = qaas.qaas_runs
            qaas_timestamp = qaas.timestamp

            arch = None
            model = None
            app_name = None
            run_data = []

            for qaas_run in qaas_runs:
                execution = qaas_run.execution
                #only add the the execution that have maqao data
                if not execution.maqaos:
                    continue
                if not arch:
                    arch = execution.hwsystem.architecture
                if not model:
                    model = execution.hwsystem.cpui_model_name
                if not app_name:
                    app_name = execution.application.workload
                MPI_threads = execution.config['MPI_threads']
                OMP_threads = execution.config['OMP_threads']
                gflops = execution.global_metrics['Gflops']
                time = execution.time
                compiler = execution.compiler_option.compiler
                vendor = compiler.vendor
                run_timestamp = execution.universal_timestamp
                run_data.append({'mpi': MPI_threads, 'omp': OMP_threads, 'gflops': gflops, 'time': time, 'compiler': vendor, 'run_timestamp': run_timestamp})
            
            data.append({'app_name': app_name, 'qaas_timestamp': qaas_timestamp, 'arch':arch, 'model': model, 'run_data': run_data})
                
        print(data[0])
        return jsonify(data)

    
    @app.route('/create_new_run', methods=['POST'])
    def create_new_run():
        #real user input data  unused for now
        qaas_request = request.get_json()
        print(qaas_request)
        script_path =  '/host/localdisk/yue/mockup_qaas.sh'
        unique_temp_dir = tempfile.mktemp()
        print(unique_temp_dir)
        result = subprocess.run(['whoami'], capture_output=True, text=True)
        print(result.stdout.strip())

        # subprocess.run([script_path, unique_temp_dir], check=True)
        # read_qaas_ov(unique_temp_dir)

        

        # ov_data_dir = os.path.join(config['web']['QAAS_DATA_FOLDER'], 'ov_data')
        # os.makedirs(ov_data_dir, exist_ok=True)
        # json_file = config['web']['INPUT_JSON_FILE']
        
        # #call backplane and wait to finish
        # t = QaaSThread(json_file, config['web']['QAAS_DATA_FOLDER'], qaas_message_queue)
        # t.start()
        # t.join()
        
        # output_ov_dir = t.output_ov_dir
        #output_ov_dir = "/nfs/site/proj/alac/tmp/qaas-fix/tmp/qaas_data/167-61-437"
        # ov_output_dir = os.path.join(output_ov_dir,'oneview_runs')
        # for version in ['opt','orig']:
        #     ov_version_output_dir = os.path.join(ov_output_dir, version)
        #     result_folders = os.listdir(ov_version_output_dir)
        #     # Should have only one folder
        #     assert len(result_folders) == 1
        #     result_folder = result_folders[0]
        #     print(result_folder)
        #     current_ov_dir = os.path.join(ov_version_output_dir, result_folder)
        #     print(f'Selected folder : {current_ov_dir}')
        #     query_time = populate_database(current_ov_dir)
        #     update_html(query_time, version)
        
        return jsonify({})
    
    ##########################run otter#####################
    @app.route('/get_html_by_timestamp', methods=['GET','POST'])
    def get_html_by_timestamp():
        #place to put files
        qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
        manifest_file_path = os.path.join(qaas_output_folder, 'input_manifest.csv')

        query_time = request.get_json()['timestamp'] 
        print("query timestamp", query_time)
        export_data(query_time, qaas_output_folder, db.session)
        create_manifest_monorun(manifest_file_path,qaas_output_folder)
        manifest_out_path = create_out_manifest(qaas_output_folder)

        run_otter_command(manifest_file_path, manifest_out_path, config)

        #get table using timestamp
        return jsonify(isError= False,
                        message= "Success",
                        statusCode= 200,
                        )




    @app.after_request
    def apply_caching(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.after_request
    def apply_hsts(response):
        response.headers["Strict-Transport-Security"] = "max-age=1024000; includeSubDomains"
        return response
    
    return app
if __name__ == '__main__':
    app = create_app(config)
    app.run(debug=True,port=5002)