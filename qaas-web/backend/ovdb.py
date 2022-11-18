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
def create_asm_table(dir_path, new_path):
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

def create_table_from_file(file_path, new_path):
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



####################################################### script start ########################        
#read manifest file
def main():
    engine = create_engine(f'mysql://moon:Jy459616!@localhost/test')
    connection = engine.connect()

    exp_dir = sys.argv[1] if len(sys.argv) > 1 else 'expR1'
    print(exp_dir)
    localvar_path = f"./{exp_dir}/static_data/local_vars.csv"

    localvar_df = pandas.read_csv(localvar_path, sep=';')
    timestamp =  pandas.to_datetime(localvar_df.get('timestamp').iloc[0])
    print("offline script timestamp pushed to db",timestamp)
    manifest_path = "./manifest.csv"
    target_path = "./file_storage/"+timestamp.strftime('%m_%d_%Y_%H_%M_%S')
    if not os.path.exists(target_path):
            os.makedirs(target_path)

    first_line = True
    with open(manifest_path,newline='') as file:
        for line in file:
            if first_line:
                first_line = False
                continue

            path = line.rstrip().split(";")[3]
            path_type = line.rstrip().split(";")[0]
            #copy binary that is not inside exp
            sub_path =  str(pathlib.Path(*Path(path).parts))
            if len(Path(path).parts) > 1:
                sub_path = str(pathlib.Path(*Path(path).parts[1:]))
            new_path = target_path +"/"+ sub_path
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            

            if path_type == "dir":
                if "asm" in path:
                    create_asm_table(path, new_path)
                # elif "cqa" in path:
                #     create_table_from_dir(path, new_path, "cqa", -9)
                # elif "groups" in path:
                #     create_table_from_dir(path, new_path, "groups", -5)
                else:
                    copyDir(path, new_path)
            elif path_type == "file": 
                create_table_from_file(path, new_path)


    manifest_df = pandas.read_csv(manifest_path, sep=';')
    print(f'pushing manifest with timestamp{timestamp}')
    manifest_df["timestamp"] = timestamp
    manifest_df['path'] = manifest_df['path'].apply(modify_path)
    manifest_df.to_sql(name= "manifest", con=engine, if_exists='append',index=False)
    localvar_df.to_sql(name= "local_vars", con=engine, if_exists='append',index=False)

#save local_vars.csv
# hierarchy should be in table and have all info
#shared data: lprof loops/functions/blocks separate tables, create 3 more col for machine name, pid, tid
#shared data: runs: add run column separate table for all csv, for global metrics only metrics table, add the number in help in metrics table
# find the timestap used in the experiment 

#asm: one table, empty if source location is nul
if __name__ == '__main__':
   main()