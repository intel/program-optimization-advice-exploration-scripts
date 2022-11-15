from glob import glob
from sqlalchemy import null
from flask import Flask
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from multiprocessing import Process, Queue
import pandas as pd
import subprocess
import json
import pandas as pd
import os
import pathlib
from pathlib import Path
import shutil
import datetime
import qaas
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# metric_map = {'time': 'shared/run_0/time.csv', 
# 'max_nb_threads': 'shared/run_0/max_nb_threads.csv',
# ...
# 'asm_dir':'static_data/asm'}

# ...
# metric='asm'
# asm_dir = os.path.join(storage_path, metric_map[metric+'_dir'])
# os.makedir(asm_dir)
# # wr file handl to write manifest.csv
# wr.println(f'dir;0;{metric+'_dir'};{asm_dir}')

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = '=true'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://moon:Jy459616!@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret!'
db = SQLAlchemy(app)
db.init_app(app)
conn = db.engine.connect().connection
db.Model.metadata.reflect(bind=db.engine,schema='test')

#socket instance with cors
CORS(app,resources={r"/*":{"origins":"*"}})

socketio = SocketIO(app, cors_allowed_origins="*")
name_space = '/test'

#can move to startup script

print("connection",conn)
def run_otter_command(manifest_file):
    cdcommand= "cd /nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example;"
    ottercommand = "maqao otter --input=" + manifest_file
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
virtual;0;executable;./mpi_hello_world;
file;0;time;./{exp_dir}/shared/run_0/time.csv;
file;0;max_nb_threads;./{exp_dir}/shared/run_0/max_nb_threads.csv;
file;0;localvars;./{exp_dir}/shared/run_0/local_vars.csv;
dir;0;lprof_dir;./{exp_dir}/shared/lprof_npsu_run_0;
dir;0;cqa_dir;./{exp_dir}/static_data/cqa;
dir;0;sources_dir;./{exp_dir}/static_data/sources;
dir;0;asm_dir;./{exp_dir}/static_data/asm;
dir;0;groups_dir;./{exp_dir}/static_data/groups;
dir;0;asm_mapping_dir;./{exp_dir}/tools/decan/run_0/others;
dir;0;hierarchy_dir;./{exp_dir}/static_data/hierarchy;
file;0;dynamic_speedup;./{exp_dir}/shared/run_0/dynamic_speedup_if.csv;
file;0;app_loops_profil;./{exp_dir}/shared/run_0/report_application_loop_profile.csv;
file;0;path_number;./{exp_dir}/shared/run_0/report_path_number_profile.csv;
file;0;static_spd;./{exp_dir}/shared/run_0/static_speedup_if.csv;
file;0;iterations;./{exp_dir}/shared/run_0/iterations_profile.csv;
file;0;spd_prompt;./{exp_dir}/shared/run_0/prompt_speedups.csv;
file;0;scala_app;./{exp_dir}/shared/run_0/scala_app.csv;
file;0;global_metrics;./{exp_dir}/shared/run_0/global_metrics.lua;
file;0;categorization;./{exp_dir}/shared/run_0/lprof_categorization.csv
file;0;application_loop_profile;./{exp_dir}/shared/run_0/report_application_loop_profile.csv"""
    with open(os.path.join(run_dir, 'manifest.csv'), 'w') as f: f.write(content)
########################### socket ########################################
@socketio.on("connect")
def connected():
    """event listener when client connects to the server"""
    print("client has connected request id is",request.sid)
    socketio.emit("connect",{"data":f"id: {request.sid} is connected"},broadcast=True)

# @socketio.on('test',namespace=name_space)
# def handle_test(data):
#     """event listener when client types a message"""
#     print("data received from the front end and send from backend: ",str(data))
#     emit("tofrontend",{'data':data,'id':request.sid},broadcast=True)

@socketio.on("disconnect")
def disconnected():
    """event listener when client disconnects to the server"""
    print("user disconnected request id is",request.sid)
    socketio.emit("disconnect",f"user {request.sid} disconnected",broadcast=True)

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

@app.route('/test_launch_button', methods=['POST'])
def test_launch_button():
    qaas_request = request.get_json()
    print(json.dumps(qaas_request))
    # event_name = 'launchButton'
    broadcast_data = "test status message"
    # socketio.emit(event_name, broadcast_data, broadcast=False, namespace=name_space)
    socketio.emit("test",{"broadcast_data":broadcast_data},broadcast=True)
    return jsonify(broadcast_data)

@app.route('/create_new_timestamp', methods=['GET','POST'])
def create_new_timestamp():
    qaas_request = request.get_json()
    print(json.dumps(qaas_request))
    ov_timestamp = int(round(datetime.datetime.now().timestamp()))
    query_time = str(datetime.datetime.fromtimestamp(ov_timestamp))
    exp_dir=f"expR1-{ov_timestamp}"
    ovcommand = f"maqao oneview -R1 -c=./config.lua -xp={exp_dir}"
    # TODO: Hardcoded for now to be passed in later
    run_dir = '/nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example'
    #subprocess.run(ovcommand, shell=True, cwd=run_dir)
    qaas_message_queue = Queue()
    qaas_launcher_process = Process(target=qaas.run_qaas, args=(qaas_message_queue, ovcommand, run_dir))
    qaas_launcher_process.start()
    while True:
        # Queue message will end up handled by
        # WebSockets or Server side event
        msg = qaas_message_queue.get()
        msg.print()
        socketio.emit("test",{"broadcast_data":msg},broadcast=True)

        # msg_type, msg_data = msg
        # print(f'{msg_type}:{msg_data}')
        if msg.web_should_stop():
            break


    qaas_launcher_process.join()
    ov_output_dir=os.path.join(run_dir, exp_dir)

    generate_manifest_csv(exp_dir, run_dir)
    print(f"Manifest file saved under: {run_dir}")
    #TODO: call it as python function directly 
    #TODO: move it out from app example directory
    ovdb_command=f'python3 ovdb.py {exp_dir}'
    subprocess.run(ovdb_command, shell=True, cwd=run_dir)
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

    otter_path = "/nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example"
    storage_path = otter_path + "/file_storage/"+pd.to_datetime(query_time).strftime('%m_%d_%Y_%H_%M_%S')
    to_delete=[]

    #get manifest file out
    manifest = db.metadata.tables['test.manifest']
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
                print(manifest_df[manifest_df['path'].str.contains(tablename)]['path'].values)
                file_absolute_path = storage_path +"/"+ manifest_df[manifest_df['path'].str.contains(tablename)]['path'].values[0]
                # print(file_absolute_path)
                file_df.to_csv(file_absolute_path, sep=';', index=False)
                to_delete.append(file_absolute_path)

          
    #get asm out
    asm_df = get_df_from_tablename_by_time('test.asm', query_time)

    #get asm path from manifest
    asm_path_query = db.session.query(manifest.c.path).filter(manifest.c.timestamp == query_time, manifest.c.path.like('%asm%'))
    asm_path = storage_path + "/" +pd.read_sql_query(asm_path_query.statement, asm_path_query.session.bind).values[0][0]
    # print("asm path ",asm_path)

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
    print(machine)
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


@app.route('/run_otter', methods=['GET','POST'])
def run_otter():
    filename = request.get_json()['filename']
    # print(filename)
    cdcommand= "cd /nfs/site/proj/alac/members/yue/source_code_with_expert/src/plugins/otter/example;"
    ottercommand = "maqao otter --input=" + filename
    command = cdcommand +  ottercommand
    ret = subprocess.run(command, capture_output=True, shell=True)
    print(ret.stdout.decode())
    return jsonify(isError= False,
                    message= "Success",
                    statusCode= 200,
                    )


@app.route("/speed_up_table")
def speed_up_table():
    expert_df = pd.read_sql_table('RESULTS/expert', db.engine)
    coverage = expert_df.loc[:,"Coverage (% app. time)"]
    cqa_no_int = expert_df.loc[:,"CQA speedup if no scalar integer"]
    cqa_fp_vec = expert_df.loc[:,"CQA speedup if FP arith vectorized"]
    cqa_full_vec = expert_df.loc[:,"CQA speedup if fully vectorized"]
    
    normalized_cov = coverage/100
    cumulative_normalized_cov = normalized_cov.cumsum()
    
    cov_div_no_int = normalized_cov / cqa_no_int
    cov_div_fp_vec = normalized_cov / cqa_fp_vec
    cov_div_full_vec = normalized_cov / cqa_full_vec
    
    cov_div_no_int_cumulative = cov_div_no_int.cumsum()
    cov_div_fp_vec_cumulative = cov_div_fp_vec.cumsum()
    cov_div_full_vec_cumulative = cov_div_full_vec.cumsum()
    
    remaining_cumulative_cov = 1 - cumulative_normalized_cov
    
    cumulative_speedup_no_int = 1 / (cov_div_no_int_cumulative + remaining_cumulative_cov/1)
    cumulative_speedup_fp_vec = 1 / (cov_div_fp_vec_cumulative + remaining_cumulative_cov/1)
    cumulative_speedup_full_vec = 1 / (cov_div_full_vec_cumulative + remaining_cumulative_cov/1)
    
    
    # print(cumulative_speedup_no_int, cumulative_speedup_fp_vec, cumulative_speedup_full_vec)
    speed_up_df={}
    speed_up_df['Number_of_Loops'] = range(1,len(expert_df)+1)
    speed_up_df['Cumlative_Speedup_No_Int'] = cumulative_speedup_no_int
    speed_up_df['Cumlative_Speedup_Fp_Vec'] = cumulative_speedup_fp_vec
    speed_up_df['Cumlative_Speedup_Fully'] = cumulative_speedup_full_vec

    speed_up_df = pd.DataFrame(speed_up_df)
    out = speed_up_df.to_json( orient='records')
    return out

@app.route("/expert")
def loops():
    expert_df = pd.read_sql_table('RESULTS/expert', db.engine)
    res_json = expert_df.to_json( orient='records')
    return res_json


if __name__ == "__main__":
    # app.run()
    print("backend starts running")
    socketio.run(app, debug=True,port=5000)
