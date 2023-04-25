from glob import glob
import pandas
from sqlalchemy import null
from flask import Flask,Response
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from multiprocessing import Process, Queue
import pandas as pd
import subprocess
import json
import pandas as pd
import os
import time
from pathlib import Path
import shutil
import datetime
import qaas
import threading
import queue
from qaas import launch_qaas
import configparser
from ovdb import populate_database, generate_manifest_csv
from flask_cors import CORS
script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../config/qaas-web.conf")
# more initializations in main()

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
    app = Flask(__name__)
    qaas_message_queue = queue.Queue()
    CORS(app)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://ov_db_with_speed_up_so:pZrYe942iKd841n@maria4344-lb-fm-in.iglb.intel.com:3307/ov_db_with_speed_up?ssl=true'
    app.config['SQLALCHEMY_DATABASE_URI'] = config['web']['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = config['web']['SECRET_KEY']

    db = SQLAlchemy(app)
    db.init_app(app)
    conn = db.engine.connect().connection
    db.Model.metadata.reflect(bind=db.engine,schema='test')


    def run_otter_command(manifest_file, version):
        cdcommand= f"cd {config['web']['EXPR_FOLDER']};"
        qaas_web_folder = os.path.join(script_dir, "../frontend/private", version)
        os.makedirs(qaas_web_folder, exist_ok=True)
        cdcommand= f"cd {qaas_web_folder};"
        ottercommand = f"{config['web']['MAQAO_VERSION']} otter --input=" + manifest_file
        command = cdcommand +  ottercommand
        print(f'Run otter command: {command}')
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stdout.decode())

    def delete_created_path(path_list):
        for path in path_list:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

    def get_df_from_tablename_by_time(tablename, query_time):
        table = db.metadata.tables[tablename]
        query = db.session.query(table).filter_by(timestamp = query_time)
        df = pd.read_sql_query(query.statement, query.session.bind)
        return df

    def get_filename(column_names, file_extension):
        filename = "_".join(column_names)
        return filename + file_extension



    ########################### http request ################################
    @app.route('/get_all_timestamps', methods=['GET','POST'])
    def get_all_timestamps():
        get_timestamp_table = db.metadata.tables['test.local_vars']
        query = db.session.query(get_timestamp_table.c.timestamp.distinct())
        timestamps = pd.read_sql_query(query.statement, query.session.bind).values
        time_list = [pd.to_datetime(timestamp[0]) for timestamp in timestamps]
        time_list = json.dumps(time_list, default=str)
        return jsonify(isError= False,
                        message= "Success",
                        timestamps= time_list,
                        statusCode= 200,
                        )
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

    @app.route('/test_launch_button', methods=['POST'])
    def test_launch_button():

        return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    )

    @app.route('/create_new_timestamp', methods=['GET','POST'])
    def create_new_timestamp():
        qaas_request = request.get_json()
        print(json.dumps(qaas_request))

        ov_data_dir = os.path.join(config['web']['QAAS_DATA_FOLDER'], 'ov_data')
        os.makedirs(ov_data_dir, exist_ok=True)
        json_file = config['web']['INPUT_JSON_FILE']
        
        #call backplane and wait to finish
        t = QaaSThread(json_file, config['web']['QAAS_DATA_FOLDER'], qaas_message_queue)
        t.start()
        t.join()
        
        output_ov_dir = t.output_ov_dir
        #output_ov_dir = "/nfs/site/proj/alac/tmp/qaas-fix/tmp/qaas_data/167-61-437"
        ov_output_dir = os.path.join(output_ov_dir,'oneview_runs')
        for version in ['opt','orig']:
            ov_version_output_dir = os.path.join(ov_output_dir, version)
            result_folders = os.listdir(ov_version_output_dir)
            # Should have only one folder
            assert len(result_folders) == 1
            result_folder = result_folders[0]
            print(result_folder)
            current_ov_dir = os.path.join(ov_version_output_dir, result_folder)
            print(f'Selected folder : {current_ov_dir}')
            query_time = populate_database(current_ov_dir)
            update_html(query_time, version)
        
        #if True:
        yellow = '\033[93m'
        reset = '\033[39;49m'
        print(f"{yellow}Finished job and html generation.{reset}")


        return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    timestamp=query_time,
                    )


    @app.route('/get_html_by_timestamp', methods=['GET','POST'])
    def get_html_by_timestamp():
        #place to put files
        query_time = request.get_json()['timestamp'] 
        update_html(query_time, 'orig')

        #get table using timestamp
        return jsonify(isError= False,
                        message= "Success",
                        statusCode= 200,
                        )

    def update_html(query_time, version):
        db.Model.metadata.reflect(bind=db.engine,schema='test')

        storage_path = os.path.join(config['web']['PERM_DATA_FOLDER'],pd.to_datetime(query_time).strftime('%m_%d_%Y_%H_%M_%S'))
        to_delete=[]

        #get manifest file out
        manifest_path = generate_manifest_csv(storage_path)
        #find manifest file that contains querytime in permanet storage 
        manifest_df = pd.read_csv(manifest_path, sep=';')
        # get local_vars out
        local_vars_df = get_df_from_tablename_by_time('test.local_vars', query_time)

        for table in db.metadata.tables:
            tablename = table.split(".")[1]
            table_type = manifest_df[manifest_df['path'].str.contains(tablename)]['type'].values[0]
            #convert all file table to file
            if table_type == "file":
                file_df = get_df_from_tablename_by_time(table, query_time).iloc[:,:-2]#none and timestamps col
                file_absolute_path = os.path.join(storage_path, manifest_df[manifest_df['path'].str.contains(tablename)]['path'].values[0])
                file_df.to_csv(file_absolute_path, sep=';', index=False)
                to_delete.append(file_absolute_path)

            
        #get asm out
        asm_df = get_df_from_tablename_by_time('test.asm', query_time)
        asm_path = os.path.join(storage_path, "static_data/asm")

        if not os.path.exists(asm_path):
                os.makedirs(asm_path)

        #create and delete
        #create asm folder files
        asm_header = ['address','source_location','insn','indent']
        unique_run = asm_df['loop_id'].unique()
        for run in unique_run:
            cur_asm_loop_df = asm_df.loc[asm_df['loop_id'] == run]
            filename_parts = []
            if cur_asm_loop_df['type'].iloc[0] == "fct":
                filename_parts.append("fct")
            if cur_asm_loop_df['decan'].iloc[0] != None:
                filename_parts.append(cur_asm_loop_df['decan'].iloc[0])
            filename_parts.append(cur_asm_loop_df['module'].iloc[0])
            filename_parts.append(cur_asm_loop_df['identifier'].iloc[0])
            cur_asm_loop_path =  asm_path + "/"+ get_filename(filename_parts, ".csv")
            # print(cur_asm_loop_path)
            cur_asm_loop_df.to_csv(cur_asm_loop_path, sep=';', index=False, columns=asm_header)
        
        run_otter_command(manifest_path, version)

        to_delete.append(asm_path)
        to_delete.append(manifest_path)
        # delete_created_path(to_delete)

    @app.route('/get_data_table_rows', methods=['GET','POST'])
    def get_data_table_rows():
        #get application, machine, and dataset
        #TODO: hardcode path
        #dataset and application in config.lua
        #machine in local_var
        #get all timestamps, for each time stamp, get machine
        get_timestamp_table = db.metadata.tables['test.local_vars']
        query = db.session.query(get_timestamp_table.c.timestamp.distinct())
        timestamps = pd.read_sql_query(query.statement, query.session.bind).values
        machines=[]
        #TODO get all machine instead of just 1
        exp_dir = config['web']['EXPR_FOLDER']
        local_vars = db.metadata.tables['test.local_vars']
        machine_query = db.session.query(local_vars.c.hostname.distinct())
        machines = pd.read_sql_query(machine_query.statement, query.session.bind).values

        machine =  machines[0][0] if len(machines) == 1 else ''
        config_path = f"{exp_dir}/config.lua"
        config_file = open(config_path, 'r')
        lines = config_file.readlines()
        application = str(lines[0].split("=")[1][2:-2])
        dataset = str(lines[1].split("=")[1][:-4])
        data={"Application":application, "Machine":machine, "Dataset":dataset}
        print(json.dumps(data) )
        return jsonify(isError= False,
                        data= json.dumps(data),
                        message= "Success",
                        statusCode= 200,
                        )

    return app

def main():
    config = configparser.ConfigParser()
    config.read(config_path)

    print("backend starts running")
    app = create_app(config)
    app.run(debug=True,port=5002)

if __name__ == "__main__":
    # app.run()
    main()
