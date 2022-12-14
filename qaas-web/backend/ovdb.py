from sqlalchemy import all_, create_engine, null
import pandas
import os
import shutil
import pathlib
from pathlib import Path
import re
import sys

#functions to append to dataframe
def clear_dataframe(df):
    df.drop(columns=df.columns, inplace=True)
    df.drop(df.index, inplace=True)

def replace_dataframe_content(to_df, from_df):
    clear_dataframe(to_df)
    for col in from_df.columns:
        to_df[col] = from_df[col]

def append_dataframe_rows(df, append_df):
    merged = df.append(append_df, ignore_index=True)
    replace_dataframe_content(df, merged)

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
    table_name = "asm"
    if engine.has_table(table_name):
        #read sql 
        old_df = pandas.read_sql(sql = table_name, con=engine)
        append_dataframe_rows(old_df, df)
        old_df.to_sql(name= table_name, con=engine, if_exists='replace',index=False)
    else:
        df.to_sql(name= table_name, con=engine, if_exists='append',index=False)

def create_table_from_file(file_path, new_path, timestamp, engine):
    if os.path.exists(file_path) ==False:
        print(file_path, " does not exist")
        return
    table_name, ext = get_tablename_and_ext_from_path(file_path)
    if ext == ".csv":
        cur_df = pandas.read_csv(file_path, sep=';')
        cur_df["timestamp"] = timestamp
        
        if engine.has_table(table_name):
            #read sql 
            old_df = pandas.read_sql(sql = table_name, con=engine)
            append_dataframe_rows(old_df, cur_df)
            old_df.to_sql(name= table_name, con=engine, if_exists='replace',index=False)
        else:
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
def generate_manifest_csv(exp_dir):
    # TODO: fix binary name hardcoded
    content=f"""type;run;usage;path;
meta;;report_type;monorun;
meta;0;run_name;run_0;
virtual;0;executable;{exp_dir}/app/oneview_runs/orig/exec;
file;0;expert_run;{exp_dir}/shared/run_0/expert_run.csv;
file;0;expert_loops;{exp_dir}/shared/run_0/expert_loops.csv;
file;0;config;{exp_dir}/shared/run_0/config.lua;
file;0;localvars;{exp_dir}/shared/run_0/local_vars.csv;
dir;0;lprof_dir;{exp_dir}/shared/lprof_npsu_run_0;
dir;0;cqa_dir;{exp_dir}/static_data/cqa;
dir;0;sources_dir;{exp_dir}/static_data/sources;
dir;0;asm_dir;{exp_dir}/static_data/asm;
dir;0;groups_dir;{exp_dir}/static_data/groups;
dir;0;hierarchy_dir;{exp_dir}/static_data/hierarchy;
file;0;global_metrics;{exp_dir}/shared/run_0/global_metrics.lua;
file;0;categorization;{exp_dir}/shared/run_0/lprof_categorization.csv;
dir;0;callchains_dir;{exp_dir}/shared/lprof_npsu_run_0/callchains;
file;0;log;{exp_dir}/logs/log.txt;
dir;0;logs_subdir;{exp_dir}/logs/run_0;
dir;0;env_dir;{exp_dir}/shared/run_0/;"""

    print("manifest file generated at ",os.path.join(exp_dir, 'manifest.csv'))
    with open(os.path.join(exp_dir,'manifest.csv'), 'w') as f: f.write(content)
    return os.path.join(exp_dir, 'manifest.csv')
def main():
    #where experimental run is default ./expR1
    if len(sys.argv) != 2:
        print(f"error, wrong number of arguments, should be 1, arguments are {sys.argv}")
        return
    run_ovdb(sys.argv[1])

def run_ovdb(exp_dir):
    import configparser
    config_path = f"{os.path.dirname(os.path.realpath(__file__))}/../config/qaas-web.conf"
    print(config_path)
    config = configparser.ConfigParser()
    config.read(config_path)
    print("config ",config.sections())
    #dialect+driver://username:password@host:port/database
    #mysql+pymysql://moon:Jy459616!@localhost/test
    # engine = create_engine(f'mysql://ov_db_with_speed_up_so:pZrYe942iKd841n@maria4344-lb-fm-in.iglb.intel.com:3307/ov_db_with_speed_up?ssl=true')
    engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI'])
    connection = engine.connect()

    print("this experiment is run in ",exp_dir)

    #permanent folder where files that are not in db are copied create if not exist

    localvar_path = f"{exp_dir}/static_data/local_vars.csv"
    localvar_df = pandas.read_csv(localvar_path, sep=';')
    timestamp =  pandas.to_datetime(localvar_df.get('timestamp').iloc[0])
    print("timestamp from path time",timestamp)

    target_path = os.path.join(config['web']['PERM_DATA_FOLDER'],timestamp.strftime('%m_%d_%Y_%H_%M_%S'))
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    manifest_path = os.path.join(exp_dir, 'manifest.csv')
    if not os.path.exists(manifest_path):
        generate_manifest_csv(exp_dir)

    first_line = True
    with open(manifest_path,newline='') as file:
        manifest_folder = os.path.dirname(manifest_path)
        for line in file:
            if first_line:
                first_line = False
                continue

            path = line.rstrip().split(";")[3]
            full_path = path if os.path.isabs(path) else exp_dir
            path_type = line.rstrip().split(";")[0].strip()
            #copy binary that is not inside exp
            sub_path =  full_path[len(exp_dir)+1:] if os.path.isabs(path) else ''
            new_path = os.path.join(target_path ,sub_path)
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

    

def populate_database(exp_dir):
    generate_manifest_csv(exp_dir)
    print(f"populate_databse manifest file saved under: {exp_dir}")
    run_ovdb(exp_dir)
    localvar_path = f"{exp_dir}/static_data/local_vars.csv"
    localvar_df = pandas.read_csv(localvar_path, sep=';')
    query_time =  pandas.to_datetime(localvar_df.get('timestamp').iloc[0])

    return query_time


if __name__ == '__main__':
   main()
