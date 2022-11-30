from sqlalchemy import all_, create_engine, null
import pandas
import os
import shutil
import pathlib
from pathlib import Path
import re
import sys

#get filename from path
def get_tablename_and_ext_from_path(file_path):
    table_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1]
    return table_name, ext

#get all csv file from dir and cp files to des if not 
def get_all_csv_from_dir( path, new_path, ext='.csv' ):
    all_csv = []
    for root, dirs, files in os.walk(path):
        for file in files:
            cur_path = os.path.join(root, file)
            _, extension = os.path.splitext(cur_path)
            if extension != ext:
                shutil.copyfile(cur_path, new_path)
            else:
                all_csv.append(cur_path)
    return all_csv
def get_loop_id(filename):
    nums_in_filename = [int(s) for s in filename.split("_") if s.isdigit()]
    if len(nums_in_filename) > 0:
        return nums_in_filename[0]
    else:
        return -1
def create_asm_table(dir_path, new_path, timestamp, engine):
    #add timestamps as foriegn key, and table id as a primary key
    # when access/filter will 
    if os.path.exists(dir_path) ==False:
        print(dir_path, " does not exist")
        return
    all_csv_path = get_all_csv_from_dir(dir_path, new_path)
    dfs = []
    for csv_path in all_csv_path:
        filename, ext = get_tablename_and_ext_from_path(csv_path)
        cur_df = pandas.read_csv(csv_path, sep=';')
        #general column
        cur_df["loop_id"] = get_loop_id(filename)
        cur_df["timestamp"] = timestamp

        #specific to each table
        fn_parts = filename.split("_")
        decans = ["DL1", "FES","FP","LS","ORIG","REF"]
        file_type = fn_parts[0]
        cur_df["type"] = "loop"
        cur_df["decan"] = None
        cur_df["module"] = "_".join(fn_parts[1:-1])
        cur_df["identifier"] = fn_parts[-1]
        if file_type in decans:
            cur_df["decan"] = file_type
        elif file_type == 'fct':
            cur_df["type"] = "fct"
        else:
            cur_df["module"] = "_".join(fn_parts[0:-1])   
        dfs.append(cur_df)
    df = pandas.concat(dfs)
    df.to_sql(name= "asm", con=engine, if_exists='append',index=False)

def create_table_from_file(file_path, new_path, timestamp, engine):
    if os.path.exists(file_path) ==False:
        print(file_path, " does not exist")
        return
    table_name, ext = get_tablename_and_ext_from_path(file_path)
    if ext == ".csv":
        cur_df = pandas.read_csv(file_path, sep=';')
        cur_df["timestamp"] = timestamp
        cur_df.to_sql(name= table_name, con=engine, if_exists='append',index=False)
    else:
        shutil.copyfile(file_path, new_path)
def copyDir(from_path, to_path):
    if os.path.exists(from_path) ==False:
        print(from_path, " does not exist")
        return
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)




#create manifest table
def modify_path(path):
    sub_path =  str(pathlib.Path(*Path(path).parts))
    if len(Path(path).parts) > 1:
        sub_path = str(pathlib.Path(*Path(path).parts[1:]))
    # cleaned_path = target_path+ "/"+sub_path
    cleaned_path = sub_path
    # print(sub_path)

    # cleaned_path = sub_path
    return cleaned_path

def main():
    #where experimental run is default ./expR1
    exp_dir = sys.argv[1] if len(sys.argv) > 1 else 'expR1'
    run_dir = sys.argv[2]

    run_ovdb(exp_dir, run_dir)

def run_ovdb(exp_dir, run_dir):
    import configparser
    config_path = f"{os.path.dirname(os.path.realpath(__file__))}/../config/qaas-web.conf"
    print(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    print("config ",config.sections())
    #dialect+driver://username:password@host:port/database
    #mysql+pymysql://moon:Jy459616!@localhost/test
    # engine = create_engine(f'=true')
    engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI'])
    connection = engine.connect()

    print("this experiment is run in ",exp_dir)

    localvar_path = f"{os.path.join(run_dir, exp_dir)}/static_data/local_vars.csv"
    localvar_df = pandas.read_csv(localvar_path, sep=';')
    timestamp =  pandas.to_datetime(localvar_df.get('timestamp').iloc[0])
    print("timestamp extraced from experimental run local var csv",timestamp)
    manifest_path = f"{run_dir}/manifest.csv"

    #where files that are not in db are copied create if not exist
    target_path = os.path.join(config['web']['PERM_DATA_FOLDER'],timestamp.strftime('%m_%d_%Y_%H_%M_%S'))
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    first_line = True
    with open(manifest_path,newline='') as file:
        manifest_folder = os.path.dirname(manifest_path)
        for line in file:
            if first_line:
                first_line = False
                continue

            path = line.rstrip().split(";")[3]
            full_path = path if os.path.isabs(path) else os.path.join(manifest_folder, path)
            path_type = line.rstrip().split(";")[0].strip()
            #copy binary that is not inside exp
            sub_path =  str(pathlib.Path(*Path(path).parts))
            if len(Path(path).parts) > 1:
                sub_path = str(pathlib.Path(*Path(path).parts[1:]))
            new_path = target_path +"/"+ sub_path
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            

            if path_type == "dir":
                if "asm" in path:
                    create_asm_table(full_path, new_path, timestamp, engine)
                # elif "cqa" in path:
                #     create_table_from_dir(path, new_path, "cqa", -9)
                # elif "groups" in path:
                #     create_table_from_dir(path, new_path, "groups", -5)
                else:
                    copyDir(full_path, new_path)
            elif path_type == "file": 
                create_table_from_file(full_path, new_path, timestamp, engine)

    manifest_df = pandas.read_csv(manifest_path, sep=';')
    manifest_df["timestamp"] = timestamp
    manifest_df['path'] = manifest_df['path'].apply(modify_path)
    manifest_df.to_sql(name= "manifest", con=engine, if_exists='append',index=False)
    localvar_df.to_sql(name= "local_vars", con=engine, if_exists='append',index=False)

def populate_database(exp_dir, run_dir):
    generate_manifest_csv(exp_dir, run_dir)
    print(f"Manifest file saved under: {run_dir}")
    #ovdb_command=f'python3 {script_dir}/ovdb.py {exp_dir} {run_dir} '

    #subprocess.run(ovdb_command, shell=True, cwd=run_dir)
    run_ovdb(exp_dir, run_dir)

    localvar_path = f"{run_dir}/{exp_dir}/static_data/local_vars.csv"
    localvar_df = pandas.read_csv(localvar_path, sep=';')
    query_time =  pandas.to_datetime(localvar_df.get('timestamp').iloc[0])
    print("flask query time extraced from local var", query_time)
    return query_time

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

if __name__ == '__main__':
   main()
