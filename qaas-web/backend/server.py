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
from settings import PERM_DATA_FOLDER
from flask_cors import CORS

qaas_data_folder = "/tmp/qaas_data"
script_dir=os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)
CORS(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = '=true'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://moon:Jy459616!@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'
db = SQLAlchemy(app)
db.init_app(app)
conn = db.engine.connect().connection
db.Model.metadata.reflect(bind=db.engine,schema='test')

#can move to startup script

def run_otter_command(manifest_file):
    cdcommand= "cd /nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example;"
    ottercommand = "/nfs/site/proj/alac/software/UvsqTools/20221102/bin/maqao otter --input=" + manifest_file
    command = cdcommand +  ottercommand
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
def generate_manifest_csv(exp_dir, run_dir):
    # TODO: fix binary name hardcoded
    content=f"""type;run;usage;path;
meta;;report_type;monorun;
meta;0;run_name;run_0;
virtual;0;executable;./{exp_dir}/app/oneview_runs/orig/exec;
file;0;expert_run;./{exp_dir}/shared/run_0/expert_run.csv;
file;0;expert_loops;./{exp_dir}/shared/run_0/expert_loops.csv;
file;0;config;./{exp_dir}/shared/run_0/config.lua;
file;0;localvars;./{exp_dir}/shared/run_0/local_vars.csv;
dir;0;lprof_dir;./{exp_dir}/shared/lprof_npsu_run_0;
dir;0;cqa_dir;./{exp_dir}/static_data/cqa;
dir;0;sources_dir;./{exp_dir}/static_data/sources;
dir;0;asm_dir;./{exp_dir}/static_data/asm;
dir;0;groups_dir;./{exp_dir}/static_data/groups;
dir;0;hierarchy_dir;./{exp_dir}/static_data/hierarchy;
file;0;global_metrics;./{exp_dir}/shared/run_0/global_metrics.lua;
file;0;categorization;./{exp_dir}/shared/run_0/lprof_categorization.csv;
dir;0;callchains_dir;./{exp_dir}/shared/lprof_npsu_run_0/callchains;
file;0;log;./{exp_dir}/logs/log.txt;
dir;0;logs_subdir;./{exp_dir}/logs/run_0;
dir;0;env_dir;./{exp_dir}/shared/run_0/;"""

    print("manifest file generated at ",os.path.join(run_dir, 'manifest.csv'))
    with open(os.path.join(run_dir,'manifest.csv'), 'w') as f: f.write(content)


########################### http request ################################
@app.route('/get_all_timestamps', methods=['GET','POST'])
def get_all_timestamps():
    manifest = db.metadata.tables['test.manifest']
    query = db.session.query(manifest.c.timestamp.distinct())
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
            time.sleep(1)
            yield f'event: ping\ndata: {datetime.datetime.now().second} \n\n'

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
    # print(json.dumps(qaas_request))
    ov_timestamp = int(round(datetime.datetime.now().timestamp()))
    query_time = str(datetime.datetime.fromtimestamp(ov_timestamp))
    # import time
    # time.sleep(20)
    exp_dir=f"expR1-{ov_timestamp}"
    ovcommand = f"maqao oneview -R1 -c=./config.lua -xp={exp_dir}"
    # TODO: Hardcoded for now to be passed in later
    run_dir = '/nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example'
    #subprocess.run(ovcommand, shell=True, cwd=run_dir)

    ov_data_dir = os.path.join(qaas_data_folder, 'ov_data')
    os.makedirs(ov_data_dir, exist_ok=True)
    json_file = os.path.join(ov_data_dir, 'input-cnn.json')
    shutil.copy('/nfs/site/proj/alac/members/yue/qaas/qaas/demo/json_inputs/input-cnn.json', json_file)
    qaas_message_queue = queue.Queue()
    t = threading.Thread(target=launch_qaas, args=(json_file, lambda msg: qaas_message_queue.put(msg), qaas_data_folder))
    t.start()
    while True:
        # Queue message will end up handled by
        # WebSockets or Server side event
        msg = qaas_message_queue.get()
        print(msg.str())
        if msg.is_end_qaas():
            output_ov_dir = msg.output_ov_dir
            break
    t.join()
    ov_output_dir = os.path.join(output_ov_dir,'oneview_runs')
    for version in ['orig', 'opt']:
        ov_version_output_dir = os.path.join(ov_output_dir, version)
        result_folders = os.listdir(ov_version_output_dir)
        # Should have only one folder
        assert len(result_folders) == 1
        result_folder = result_folders[0]
        print(result_folder)
        current_ov_dir = os.path.join(ov_version_output_dir, result_folder)
    
    if True:
        # current_ov_dir = '/tmp/qaas_data/166-56-642/oneview_runs/orig/oneview_results_1668569657'
        print(f'Selected folder : {current_ov_dir}')
        full_exp_dir = os.path.join(run_dir, exp_dir)
        shutil.copytree(current_ov_dir, full_exp_dir)
        print(f'exp:{full_exp_dir}')    
    
    # qaas_message_queue = Queue()
    # qaas_launcher_process = Process(target=qaas.run_qaas, args=(qaas_message_queue, ovcommand, run_dir))
    # qaas_launcher_process.start()
    # while True:
    #     # Queue message will end up handled by
    #     # WebSockets or Server side event
    #     msg = qaas_message_queue.get()
    #     msg.print()
    #     socketio.emit("test",{"broadcast_data":msg},broadcast=True)

    #     # msg_type, msg_data = msg
    #     # print(f'{msg_type}:{msg_data}')
    #     if msg.web_should_stop():
    #         break



    # qaas_launcher_process.join()
    ov_output_dir=os.path.join(run_dir, exp_dir)

    generate_manifest_csv(exp_dir, run_dir)
    print(f"Manifest file saved under: {run_dir}")
    #TODO: call it as python function directly 
    #TODO: move it out from app example directory
    ovdb_command=f'python3 {script_dir}/ovdb.py {exp_dir} {run_dir} '

    subprocess.run(ovdb_command, shell=True, cwd=run_dir)

    localvar_path = f"{run_dir}/{exp_dir}/static_data/local_vars.csv"
    localvar_df = pandas.read_csv(localvar_path, sep=';')
    query_time =  pandas.to_datetime(localvar_df.get('timestamp').iloc[0])
    print("flask query time extraced from local var", query_time)
    update_html(query_time)



    return jsonify(isError= False,
                message= "Success",
                statusCode= 200,
                timestamp=query_time,
                )

@app.route('/get_html_by_timestamp', methods=['GET','POST'])
def get_html_by_timestamp():
    #place to put files
    query_time = request.get_json()['timestamp'] 
    update_html(query_time)

    #get table using timestamp
    return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    )

def update_html(query_time):
    db.Model.metadata.reflect(bind=db.engine,schema='test')

    otter_path = "/nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example"
    storage_path = os.path.join(PERM_DATA_FOLDER,pd.to_datetime(query_time).strftime('%m_%d_%Y_%H_%M_%S'))
    to_delete=[]

    #get manifest file out
    manifest = db.metadata.tables['test.manifest']
    print(f"manifest query time : {query_time}")
    manifest_df = get_df_from_tablename_by_time('test.manifest', query_time)
    # get local_vars out
    local_vars_df = get_df_from_tablename_by_time('test.local_vars', query_time)

    for table in db.metadata.tables:
        tablename = table.split(".")[1]
        if tablename != "manifest":
            table_type = manifest_df[manifest_df['path'].str.contains(tablename)]['type'].values[0]
            #convert all file table to file
            if table_type == "file":
                file_df = get_df_from_tablename_by_time(table, query_time).iloc[:,:-2]#none and timestamps col
                file_absolute_path = storage_path +"/"+ manifest_df[manifest_df['path'].str.contains(tablename)]['path'].values[0]
                file_df.to_csv(file_absolute_path, sep=';', index=False)
                to_delete.append(file_absolute_path)

          
    #get asm out
    asm_df = get_df_from_tablename_by_time('test.asm', query_time)

    #get asm path from manifest
    asm_path_query = db.session.query(manifest.c.path).filter(manifest.c.timestamp == query_time, manifest.c.path.like('%asm%'))
    asm_path = storage_path + "/" +pd.read_sql_query(asm_path_query.statement, asm_path_query.session.bind).values[0][0]

    if not os.path.exists(asm_path):
            os.makedirs(asm_path)

    #create and delete
    #create manifest file
    manifest_path=storage_path+"/"+"manifest.csv"
    manifest_header = ['type','run','usage','path']
    manifest_df['path'] = manifest_df['path'].apply(lambda path: storage_path+"/" + path)
    manifest_df.to_csv(manifest_path, sep=';', index=False, columns=manifest_header)
    local_vars_df.to_csv(storage_path+"/local_vars.csv", sep=';', index=False)

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
    
    run_otter_command(manifest_path)

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
    manifest = db.metadata.tables['test.manifest']
    query = db.session.query(manifest.c.timestamp.distinct())
    timestamps = pd.read_sql_query(query.statement, query.session.bind).values
    machines=[]
    #TODO get all machine instead of just 1
    exp_dir = "/nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example"
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


if __name__ == "__main__":
    # app.run()
    print("backend starts running")
    app.run(debug=True,port=5002)
