import pandas as pd
import os
import numpy as np
import subprocess
from slpp import slpp as lua
import struct
from model import *
import math
import re
from datetime import datetime
import configparser
import numpy as np
import tempfile
import builtins
import shutil
import configparser
import shlex

####constants
level_map = {0: 'Single', 1: 'Innermost', 2: 'InBetween', 3: 'Outermost'}
reverse_level_map = {v: k for k, v in level_map.items()}

## helper functions
def safe_division(n, d):
    if n is None or d is None:
        return None
    return n / d
def is_df_empty(df):
    return df.applymap(lambda x: x is None).all().all()

def delete_nan_from_dict(dict):
    return {k: v for k, v in dict.items() if not (isinstance(v, float) and math.isnan(v))}



def get_config():
    SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", '..',"config", "qaas-web.conf")
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(CONFIG_PATH)
    return config


################################### run otter ###########################
def create_manifest_file_for_run(run_id, run_name, output_data_dir, manifest_path):
    content =  f"""meta;{run_id};run_name;{run_name};
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

def create_manifest_comparison(manifest_path, output_data_dir_list, timestamp_list, session):
    if os.path.isfile(manifest_path):
        os.remove(manifest_path)
    write_manifest_header(manifest_path, 'multirun')
    index = 0
    for output_data_dir, query_time in zip(output_data_dir_list, timestamp_list):
        base_run_name = get_base_run_name(query_time, session)
        create_manifest_file_for_run(index, base_run_name, output_data_dir, manifest_path)
        index += 1
def get_base_run_name(query_time, session):
    current_execution = Execution.get_obj(query_time, session)
    base_run_name = current_execution.config['base_run_name']
    return base_run_name
def create_manifest_monorun(manifest_path, output_data_dir, query_time, session):
    if os.path.isfile(manifest_path):
        os.remove(manifest_path)
    write_manifest_header(manifest_path, 'monorun')
    base_run_name = get_base_run_name(query_time, session)

    create_manifest_file_for_run(0, base_run_name, output_data_dir, manifest_path)

def run_otter_command(manifest_file_path, out_manifest_path, config):
    run_dir = os.path.dirname(manifest_file_path)
    cdcommand= f"cd {run_dir};"
    ottercommand = f"{config['web']['MAQAO_VERSION']} otter --input={manifest_file_path} --output={out_manifest_path}"  
    # command = cdcommand +  ottercommand
    print(ottercommand)
    # Use this version for SDP because flagging for shell=True
    ret = subprocess.run([config['web']['MAQAO_VERSION'], "otter", f"--input={manifest_file_path}", f"--output={out_manifest_path}"], cwd=run_dir, capture_output=True)
    
    # This is original implementation
    # ret = subprocess.run(command, capture_output=True, shell=True)
    print(ret.stdout.decode())
   

####### datatype converstion ##########
def convert_lua_to_python(lua_file):
    if os.path.exists(lua_file):
    #     return compress_file(lua_file)
        with open(lua_file, 'r') as file:
            file_str = file.read()
        file_str = '{' + file_str + '}'
        dic = lua.decode(file_str)
        return dic

def convert_python_to_lua(python_object,lua_file_path):
    if python_object:
    #     with open(lua_file_path, 'wb') as f:
    #         f.write(decompress_file(python_object))
    #use slpp library instead of write the string
        if os.path.basename(lua_file_path) == 'config.lua':
            keys = list(python_object.keys())
            values = list(python_object.values())
            with open(lua_file_path, 'w') as file:
                for key, value in zip(keys, values):
                    value = lua.encode(value)
                    line = f"{key} = {value}\n"
                    file.write(line)
        else:
            key = list(python_object.keys())[0]
            value = list(python_object.values())[0]
            lua_str = lua.encode(value)
            lua_str = f'{key} = {lua_str}'
            with open(lua_file_path, 'w') as file:
                file.write(lua_str)
def convert_text_to_dict(text_file):
    with open(text_file, "r") as f:
        my_dict = {}
        for line in f:
            # Split the line into key and value using "=" as the separator
            key, value = line.strip().split("=", maxsplit=1)
            # If the value contains more than one line, read until the next key
            while value.endswith("\\"):
                value = value[:-1] + f.readline().strip()
            # Add the key-value pair to the dictionary
            my_dict[key] = value
        return my_dict
def universal_timestamp_to_datetime(universal_timestamp):
    return datetime.fromtimestamp(int(universal_timestamp)).strftime("%c")
def datetime_to_universal_timestamp(date_time):
    return str(int(datetime.strptime(date_time, '%c').timestamp()))

#### create/update/get/parse 
#used to read the qaas metadata file
def get_config_from_path(path):
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(path)
    return config

def parse_text_to_dict(file_path):
    data_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            # split by =
            parts = line.strip().split('=')
            if len(parts) == 2:
                key, value = parts
                data_dict[key] = value
    return data_dict

def parse_experiment_name(experiment_name):
    pattern = r'(orig|unicore/([^/_]*))'
    match = re.search(pattern, experiment_name)
    if match:
        return match.group(2) if match.group(2) else match.group(1)
    else:
        return None
def get_files_with_pattern(directory, pattern):
    files = []
    for file in os.listdir(directory):
        match = re.match(pattern, file)
        if match:
            files.append(file)
    
    return files
def parse_file_name(file_name):
    match = re.match(r'^(?:(fct|src)_)?(?:([A-Z0-9]+)_)?(.*?_(\d+))(?:_cqa)?(?:_text)?(?:\.csv)?(?:\.txt)?(?:\.lua)?$', file_name)
    if match:
        prefix = match.group(1)
        variant = match.group(2)
        module_and_id = match.group(3)
        # Separate module and id from the combined string
        module, identifier = module_and_id.rsplit('_', 1)
        if prefix == "fct":
            type = 1
        else:
            type = 0
        return type, variant, module, identifier
    else:
        return None

#this funciton is used to get path from input manifest using usage type
def get_path_from_input_manifest_df(df, usage_type, qaas_data_dir):
    filtered_df = df[df['usage'] == usage_type]
    if not filtered_df.empty:
        path = filtered_df.iloc[0]['path']
        match = re.search(r'oneview_results_\d+/|private(/\d+)?/', path)
        if match:
            start_index = match.end()
            return os.path.join(qaas_data_dir,path[start_index:])
    return None

def get_run_path_and_id(path):
    path_parts = path.split("/")
    run_component = next((part for part in path_parts if "run_" in part), None)
    run_id = None
    if run_component:
        run_id = run_component.split("_")[1]

    if run_component:
        sub_path_index = path_parts.index(run_component)
        sub_path = "/".join(path_parts[:sub_path_index+1])

    return run_id, sub_path
def get_all_functions_for_run(modules):
    res = []
    for module in modules:
        functions = module.functions
        res.extend(functions)
    return res
def get_all_loops_for_run(functions):
    res = []
    for function in functions:
        loops = function.loops
        res.extend(loops)
    return res
def get_all_lprof_measure_for_run(blocks, functions, loops):
    res = []
    for block in blocks:
        res.extend(block.lprof_measurements)
    for function in functions:
        res.extend(function.lprof_measurements)
    for loop in loops:
        res.extend(loop.lprof_measurements)
    return res

def get_all_cqa_for_run(functions, loops):
    res = []
    for function in functions:
        if function.cqa_measures:
            res.extend(function.cqa_measures)
    for loop in loops:
        if loop.cqa_measures:
            res.extend(loop.cqa_measures)
    return res
def get_all_asm_for_run(functions, loops):
    res = []
    for function in functions:
        if function.asms:
            res.extend(function.asms)
    for loop in loops:
        if loop.asms:
            res.extend(loop.asms)
    return res

def get_all_source_for_run(execution):
    src_functions = execution.src_functions
    src_loops = execution.src_loops
    res = []
    for src_function in src_functions:
        if src_function.source:
            src = src_function.source
            res.append(src)
    for src_loop in src_loops:
        if src_loop.source:
            src = src_loop.source
            res.append(src)
    return res

def get_all_groups_for_run(loops):
    res = []
    for loop in loops:
        if loop.groups:
            res.extend(loop.groups)
    return res


def get_function_by_source_function(src_function, functions):
    res = None
    for function in functions:
        if function.src_function == src_function:
            return function
    return res

def get_global_metrics_dict_from_execution(execution):
    return pd.read_json(execution.global_metrics['global_metrics'], orient="split").set_index('metric')['value'].to_dict()


def get_all_loops_from_src_loops(src_loops):
    loops = []
    for src_loop in src_loops:
        loops.extend(src_loop.loops)
    unique_loops = list(set(loops))
    return unique_loops
def get_loop_by_source_loop(src_loop, loops):
    res = None
    for loop in loops:
        if loop.src_loop == src_loop:
            return loop
    return res

def create_html_lua_by_text_python(analysis_python_data, analysis_html_lua_path):
    convert_python_to_lua(analysis_python_data,analysis_html_lua_path)

    #TODO change to process instead of just writeing the same data
    # output_dict = process_nested_dict(analysis_python_data)
    # convert_python_to_lua(output_dict,analysis_html_lua_path)

def get_all_functions(loop_collection):
    all_loops = loop_collection.get_objs()
    function_set = set()
    for loop in all_loops:
        function_set.add(loop.function)
    return function_set

def add_dict_to_df(dict_to_append, df):        
    df_to_append = pd.DataFrame(dict_to_append, index=[0])
    df = pd.concat([df, df_to_append], ignore_index=True)
    return df

def combine_source_info(source_name, line_number):
    if not source_name and not line_number:
        return None
    source_files = source_name.split(',')
    line_numbers = line_number.split(',')

    if len(source_files) != len(line_numbers):
        raise ValueError("The number of source files must match the number of line numbers.")

    combined = [f'{file.strip()}:{line.strip()}' for file, line in zip(source_files, line_numbers)]
    
    return ','.join(combined)
def accumulate_df(df, keys, out_file):
    if os.path.exists(out_file):
        cur_df = read_file(out_file)
        df = merge_df(cur_df, df, [c for c in df.columns if c not in keys], keys)
    write_file(df, out_file)

# Adapted from CapeScripts: https://gitlab.com/davidwong/cape-experiment-scripts/-/blob/master/base/capelib.py
def merge_df(to_df, from_df, cols, keys):
    for key in keys:
        to_df[key] = to_df[key].astype(str)
        from_df[key] = from_df[key].astype(str)
    merged = pd.merge(left=to_df, right=from_df[keys+list(cols)], on=keys, how='left')      
    # merged = merged.set_index(to_df.index)
    for col in cols:
        if col + "_y" in merged.columns and col + "_x" in merged.columns:
            # _y is incoming df data so use it and fill in _x (original) if missing
            merged[col] = merged[col + "_y"].fillna(merged[col + "_x"])
        to_df[col] = merged[col]
    return to_df

def get_names_and_values_data_for_metric_table(metrics):
    data = {}
    for metric in metrics:
        data[metric.metric_name] = metric.metric_value 
    return data
def read_file(path, delimiter=';'):
    df = pd.read_csv(path, sep=delimiter, keep_default_na=False, index_col=False, skipinitialspace=True, na_values=[''])
    df = df.replace({np.nan: None})
    return df

def write_file(df, path, delimiter=';'):
    df.to_csv(path, sep=delimiter, index=False, header=True)
def read_file(path, delimiter=';'):
    df = pd.read_csv(path, sep=delimiter, keep_default_na=False, index_col=False, skipinitialspace=True, na_values=[''])
    df = df.replace({np.nan: None})
    return df

def get_or_create_df(path):
    if os.path.exists(path):
        df = read_file(path)
    else:
        df = pd.DataFrame()
    return df
def write_dict_to_file(my_dict, filename):
    with open(filename, "w") as f:
        for key, value in my_dict.items():
            # If the value contains newline characters, replace them with "\n"
            value = value[0].replace("\n", "\\n")
            # Write the key-value pair to the file
            f.write(f"{key}={value}\n")

def create_or_update_localvar_df(metric, value, file_path):
    try:
        df = pd.read_csv(file_path, sep=';', index_col=None)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['metric', 'value'])

 
    new_data = pd.DataFrame({'metric': [metric], 'value': [value]})
    df = pd.concat([df, new_data], ignore_index=True)

    df.to_csv(file_path, sep=';', index=False)

def get_files_with_extension(directory, extensions):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(tuple(extensions)) :
            files.append(os.path.join(directory, filename))
    return files
def get_function(functions, function_id,pid, tid, module, function_name):
    res = None
    for function in  functions:
        cur_module = os.path.basename(function.module.name) if function.module else None
        cur_function_name = function.function_name
        if function.maqao_function_id == function_id and function.pid == pid and function.tid == tid and module == cur_module and function_name == cur_function_name:
            return function
    return res
def get_loop(loops, loop_id,pid, tid):
    res = None
    for loop in  loops:
        if loop.maqao_loop_id == loop_id and loop.pid == pid and loop.tid == tid:
            return loop
    return res
def get_lprof_measure(lprof_measures, block=None, function=None, loop=None):
    res = None
    for lprof_measure in lprof_measures:
        if lprof_measure.block == block and lprof_measure.function == function and lprof_measure.loop == loop:
            return lprof_measure
    return res
def get_block(blocks, block_id,pid, tid):
    res = None
    for block in  blocks:
        if block.maqao_block_id == block_id and block.pid == pid and block.tid == tid:
            return block
    return res
def parse_source_info(source_info):
    if not source_info:
        return None, None
    source_files = []
    line_numbers = []

    split_info = source_info.split(',')
    for info in split_info:
        source_name, line_number = info.split(':')
        source_files.append(source_name.strip())
        line_numbers.append(line_number.strip())

    source_files = ','.join(source_files)
    line_numbers = ','.join(line_numbers)

    return source_files, line_numbers

def get_all_functions_from_src_functions(src_functions):
    functions = []
    for src_function in src_functions:
        functions.extend(src_function.functions)
    unique_functions = list(set(functions))
    return unique_functions

def get_files_starting_with_and_ending_with(directory, prefix, suffix):
    files = os.listdir(directory)
    filtered_files = [os.path.join(directory, file) for file in files if file.startswith(prefix) and file.endswith(suffix)]
    return filtered_files

def get_data_from_csv(csv_path):
    num_cols = len(open(csv_path).readline().split(';'))
    if num_cols <= 1:
        return None
    data = pd.read_csv(csv_path,sep=';',index_col=None,skipinitialspace=True,usecols=range(num_cols - 1)).to_dict(orient='records')
    return data

def get_table_data_from_df(df, Table):
    columns = get_columns(Table)
    data = df.reindex(columns, axis=1).to_dict(orient='records')
    
    # Remove nan values from each dictionary
    cleaned_data = [delete_nan_from_dict(record) for record in data]
    
    return cleaned_data

def get_module_by_name(modules, module_name):
    return [m for m in modules if os.path.basename(m.name) == module_name][0]
def get_src_function_by_file_and_line_nb(src_functions, file, line_number):
    res = [sf for sf in src_functions if sf.file == file and sf.line_number == line_number]
    return res[0] if res else None
def get_function_by_maqao_id(current_execution, maqao_id):
    res = None
    for src_function in current_execution.src_functions:
        for f in src_function.functions:
            if f.maqao_function_id == maqao_id:
                return f
    return res
def get_loop_by_maqao_id(current_execution, maqao_id):
    res = None
    for src_loop in current_execution.src_loops:
        for l in src_loop.loops:
            if l.maqao_loop_id == maqao_id:
                return l
    return res




def get_obj_by_tid_and_pid(objs, pid, tid):
    res = []
    for obj in objs:
        if obj.pid == pid and obj.tid == tid:
            res.append(obj)
    return res




###### df and dict opreations
def get_columns(table):
    return [column.name for column in table.__table__.columns if not column.primary_key and not column.foreign_keys]

def get_extra_columns(table):
    return [column.name for column in table.__table__.columns if column.primary_key or column.foreign_keys ]



def get_df_from_path(file_path):
    try:
        cur_df = pd.read_csv(file_path, sep=';')
    except pd.errors.EmptyDataError:
        cur_df = pd.DataFrame()
    return cur_df
def get_lprof_measure_df_from_obj(cur_measures):
    new_df = []
    for current_measure in cur_measures:
        if current_measure:
            measure_dict = {
                'time_p' : current_measure.time_p,
                'time_s' : current_measure.time_s, 
                'time_s_min' : current_measure.time_s_min,
                'time_s_max' : current_measure.time_s_max, 
                'time_s_avg' : current_measure.time_s_avg, 
                'cov_deviation' : current_measure.cov_deviation,
                'time_deviation' : current_measure.time_deviation,
                'nb_threads' : current_measure.nb_threads, 
            }
            
        else:
            measure_dict = {
                'time_p' : '',
                'time_s' : '', 
                'time_s_min' : '',
                'time_s_max' : '', 
                'time_s_avg' : '', 
                'cov_deviation' : '',
                'time_deviation' : '',
                'nb_threads' : '', 
            }
        new_df.append(measure_dict)
    new_df = pd.DataFrame(new_df)
    return new_df




###### binary file reading functions
def read_int(file):
    data = file.read(4)
    if len(data) != 4:
        #could be end of the file
        return -1
    return struct.unpack("<i", data)[0]
def read_double(file):
    data = file.read(8)
    if len(data) != 8:
        return -1
    return struct.unpack("<d", data)[0]
def decode_string(data):
    return data.decode('utf-8')

def read_dictionary(strings_count, f, session):
    strings = {}
    for i in range(strings_count):
        string_size = read_int(f)
        string_bytes = f.read(string_size)
        string_value = decode_string(string_bytes)
        table_id = StringClass.get_or_create_table_id_by_string(string_value, session)
        strings[i+1] = string_value
    return strings

def read_intervals(source_file_intervals_count, f):
     source_file_intervals = []
     for j in range(source_file_intervals_count):
            interval_start_line = read_int(f)
            interval_stop_line = read_int(f)
            source_file_intervals.append((interval_start_line, interval_stop_line))
     return source_file_intervals

def read_src_file(regions_count, f, strings, session):
    src_files = []

    for i in range(regions_count):
    # source file section of the object
        file_index = read_int(f)
        file_index = StringClass.get_or_create_table_id_by_string(strings[file_index], session)
        source_file_intervals_count = read_int(f)
        source_file_intervals = read_intervals(source_file_intervals_count, f)
        src_file_data={
            'source_file_index':file_index,
            'source_file_intervals':source_file_intervals
        }
        src_files.append(src_file_data)
    return src_files


def read_objects(binary_format_version, objects_count, f, strings, session):
    objects = []
    for i in range(objects_count):
        module_index = read_int(f)
        module_index = StringClass.get_or_create_table_id_by_string(strings[module_index], session)
        object_identifier = read_int(f)
        compilation_options_index = read_int(f)
        compilation_options_index = StringClass.get_or_create_table_id_by_string(strings[compilation_options_index], session)
        source_file_index = read_int(f)
        source_file_index = StringClass.get_or_create_table_id_by_string(strings[source_file_index], session)
        start_line = read_int(f)
        stop_line = read_int(f)
        regions_count = read_int(f)
        source_files = read_src_file(regions_count, f, strings, session)

        # Decode the object data and add it to the list of objects.
        object_data = {
            'module': module_index,
            'identifier': object_identifier,
            'compilation_options': compilation_options_index,
            'source_file': source_file_index,
            'start_line': start_line,
            'stop_line': stop_line,
            'source_file_intervals': source_files
        }

        #  exclusive regions for version 2 or higher
        if binary_format_version >= 2:
            exclusive_regions_count = read_int(f)
            exclusive_regions = read_src_file(exclusive_regions_count, f, strings, session)
            object_data['exclusive_regions'] = exclusive_regions

        objects.append(object_data)
    return objects

def read_header(f):
    # Read int (magic number)
    magic_number = read_int(f)
    if magic_number != -1:
        raise ValueError(f"Invalid magic number: {magic_number}")

    # Read 8-char magic string
    magic_string_data = f.read(8)
    if len(magic_string_data) != 8:
        raise IOError("Unexpected end of file")
    magic_string = decode_string(magic_string_data)

    # Read binary format version
    binary_format_version = read_int(f)
    return {
        'binary_format_version': binary_format_version,
    }

def convert_location_binary_to_python(binary_file_path, session):
    if not os.path.exists(binary_file_path):
        return {'headers':None, 'objects': None}
    with open(binary_file_path, 'rb') as f:
        headers = read_header(f)
        # Read the first section of the file, which contains strings.
        strings_count = read_int(f)
        strings = read_dictionary(strings_count, f, session)

        # Read the second section of the file, which contains objects.
        objects_count = read_int(f)
        objects = read_objects(headers['binary_format_version'], objects_count, f, strings, session)

    # Return the decoded data as a dictionary.
    return {'headers':headers, 'objects': objects}


def write_int(file, value):
    data = struct.pack("<i", value)
    file.write(data)

def write_double(file, value):
    data = struct.pack("<d", value)
    file.write(data)

def encode_string(string):
    return string.encode('utf-8')

def write_header(f, headers, magic_string_header):
    write_int(f, -1)
    f.write(encode_string(magic_string_header))
    write_int(f, headers['binary_format_version'])

def write_strings(f, strings):
    write_int(f, len(strings))
    for string_value in strings:
        string_data = encode_string(string_value)
        write_int(f, len(string_data))
        f.write(string_data)

def write_intervals(f, intervals):
    write_int(f, len(intervals))
    for interval_start_line, interval_stop_line in intervals:
        write_int(f, interval_start_line)
        write_int(f, interval_stop_line)

def write_source_file_intervals(f, source_file_intervals, session):
    write_int(f, len(source_file_intervals))
    for src_file in source_file_intervals:
        source_file_index = src_file['source_file_index']
        write_int(f, source_file_index)
        write_intervals(f, src_file['source_file_intervals'])

def write_objects(binary_format_version, f, objects, session):
    write_int(f, len(objects))

    for obj in objects:
        write_int(f, obj['module'])
        write_int(f, obj['identifier'])
        write_int(f, obj['compilation_options'])
        write_int(f, obj['source_file'])
        write_int(f, obj['start_line'])
        write_int(f, obj['stop_line'])
        write_source_file_intervals(f, obj['source_file_intervals'], session)
        if binary_format_version >= 2:
            write_source_file_intervals(f, obj['exclusive_regions'], session)



def add_to_set_and_list(strings_set,strings, string):
    strings_set.add(string)
    if string not in strings:
        strings.append(string)

def get_string_by_id_and_add_to_set(strings_set,strings,id, session):
    string = StringClass.get_string_by_id(id, session).string
    add_to_set_and_list(strings_set,strings, string)
    return strings.index(string) + 1

def map_and_write_strings_location(f, objects, session):
    strings_set = set()
    strings=[]
    for obj in objects:
        obj['module'] = get_string_by_id_and_add_to_set(strings_set,strings,obj['module'], session)
        obj['compilation_options'] = get_string_by_id_and_add_to_set(strings_set,strings,obj['compilation_options'], session)
        obj['source_file'] = get_string_by_id_and_add_to_set(strings_set,strings,obj['source_file'], session)
        for src_file in obj['source_file_intervals']:
            src_file['source_file_index'] = get_string_by_id_and_add_to_set(strings_set,strings,src_file['source_file_index'], session)


    return strings, objects
        

def convert_python_to_location_binary(data, binary_file_path, session):
    #don't write files if data is empty
    if data['headers'] and data['objects']:
        with open(binary_file_path, 'wb') as f:
            #still write headers even when binary is empty
            write_header(f, data['headers'],'OV_SRCLO')
            strings, objects = map_and_write_strings_location(f, data['objects'], session)
            write_strings(f, strings)
            if len(objects) > 0:
                write_objects(data['headers']['binary_format_version'], f, objects, session)

##for call chain binary
def read_callsite(callsites_count, f, strings, session):
    callsites = []
    for i in range(callsites_count):
        location_index =  read_int(f)
        location_index = StringClass.get_or_create_table_id_by_string(strings[location_index], session)
        function_identifier = read_int(f)
        module_index = read_int(f)
        module_index = StringClass.get_or_create_table_id_by_string(strings[module_index], session)
        callsite_data = {
            'location_index' : location_index,
            'function_identifier' : function_identifier,
            'module_index' : module_index
        }
        callsites.append(callsite_data)
    return callsites

def read_callchain(callchains_count, f, strings, session):
    callchains = []
    for i in range(callchains_count):
        callchain_coverage = read_double(f)
        callsites_count = read_int(f)
        callsites = read_callsite(callsites_count, f, strings, session)
        callchain_data = {
            'callchain_coverage' : callchain_coverage,
            'callsites_count' : callsites_count,
            'callsites' : callsites
        }
        callchains.append(callchain_data)
    return callchains

def convert_callchain_binary_to_python(binary_file_path, session):
    if not os.path.exists(binary_file_path):
        return  {'headers':None, 'callchains': None}
    with open(binary_file_path, 'rb') as f:
        headers = read_header(f)
        strings_count = read_int(f)
        strings = read_dictionary(strings_count, f, session)
        # Read the first section of the file, which contains strings.
        callchains_count = read_int(f)
        callchains = read_callchain(callchains_count, f, strings, session)

    # Return the decoded data as a dictionary.
    return {'headers':headers, 'callchains': callchains}

def write_callsite(f, callsites):
    for callsite in callsites:
        write_int(f, callsite['location_index'])
        write_int(f, callsite['function_identifier'])
        write_int(f, callsite['module_index'])

def write_callchains(f, callchains):
    write_int(f, len(callchains))
    for callchain in callchains:
        write_double(f, callchain['callchain_coverage'])
        write_int(f, callchain['callsites_count'])
        write_callsite(f, callchain['callsites'])

def map_and_write_strings_callchain(f, callchains, session):
    strings_set = set()
    strings=[]
    for callchain in callchains:
        callsites = callchain['callsites']
        for callsite in callsites:
            callsite['location_index'] = get_string_by_id_and_add_to_set(strings_set,strings,callsite['location_index'], session)
            callsite['module_index'] = get_string_by_id_and_add_to_set(strings_set,strings,callsite['module_index'], session)

        
    return strings, callchains

def convert_callchain_python_to_binary(data, binary_file_path, session):
        with open(binary_file_path, 'wb') as f:
            #still write headers even if the binary is empty
            write_header(f, data['headers'], "OV_CALLC")
            strings, objects = map_and_write_strings_callchain(f, data['callchains'], session)
            write_strings(f, strings)
            #only write if there are objects to write 
            if len(objects) > 0:
                write_callchains(f, objects)

# File access monitoring and copying context manager
# Usage:
#    with QaaSFileAccessMonitor(input_path, output_path) as session:
#        ....
#
# The context manager will track files being accessed under input_path and copy them to output_path
# preserving the relative path location
# it also returns a db session that can be used to for database visitor to fill in data.
class QaaSFileAccessMonitor:
    DEBUG = False
    def __init__(self, in_path, out_path, keep_db=False):
        self.accessed_files = set()
        self.full_input_path = os.path.abspath(in_path)
        self.full_output_path = os.path.abspath(out_path)
        self.keep_db = keep_db

        #connect db
        # Ensure output path exists
        os.makedirs(self.full_output_path, exist_ok=True)
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".db", prefix=f'{self.full_output_path}_', delete=False)
        db_file_name = self.temp_file.name
        self.engine = create_engine(f'sqlite:///{db_file_name}')
        #engine = create_engine('mysql://qaas:qaas@localhost/qaas')
        self.engine.connect()

        create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def __enter__(self):
        if QaaSFileAccessMonitor.DEBUG:
            print("Enter")
        self.saved_open = builtins.open
        self.saved_pd_read_csv = pd.read_csv
        builtins.open = self.my_open
        pd.read_csv = self.my_pd_read_csv
        return self.session

    def my_pd_read_csv(self, *args, **kwargs):
        self.peek_filename('filepath_or_buffer', args, kwargs)
        return self.saved_pd_read_csv(*args, **kwargs)
    
    def my_open(self, *args, **kwargs):
        self.peek_filename('file', args, kwargs)
        return self.saved_open(*args, **kwargs)

    def peek_filename(self, file_arg_name, args, kwargs):
        if file_arg_name in kwargs:
            filename = kwargs[file_arg_name]
        elif args:
            filename = args[0]
        else:
            filename = None
        full_filename=os.path.abspath(filename)
        #print(f"my open called: {filename}")
        if os.path.commonpath([self.full_input_path]) == os.path.commonpath([self.full_input_path, full_filename]):
            self.accessed_files.add(full_filename)

    def visit_file(self, full_file_path):
        if QaaSFileAccessMonitor.DEBUG:
            print(f"IN: {full_file_path}")
        rel_path = os.path.relpath(full_file_path, self.full_input_path)
        full_outfile_path = os.path.join(self.full_output_path, rel_path)
        full_outfile_dir = os.path.dirname(full_outfile_path)
        os.makedirs(full_outfile_dir, exist_ok=True)
        shutil.copy(full_file_path, full_outfile_path)
        if QaaSFileAccessMonitor.DEBUG:
            print(f"OUT: {full_outfile_dir}")

    def __exit__(self, exc_type, exc_value, traceback):
        if QaaSFileAccessMonitor.DEBUG:
            print("Exit")
        builtins.open = self.saved_open
        pd.read_csv = self.saved_pd_read_csv
        for file in sorted(self.accessed_files):
            self.visit_file(file)
            if QaaSFileAccessMonitor.DEBUG:
                print(f'FILE: {file}')

        self.session.commit()
        self.session.close()
        if not self.keep_db:
            os.unlink(self.temp_file.name)
        return False

def send_ssh_key_to_backplane(machine, password):
    user_and_machine = f"qaas@{machine}"
    home_directory = os.path.expanduser("~")
    args=["sshpass", "-e", "ssh-copy-id", "-i", f"{home_directory}/.ssh/id_rsa.pub", "-o", "StrictHostKeyChecking=no", user_and_machine, "-p", "2222" ]
    # Use shlex.quote() sanitize inputs
    args_shlex = [shlex.quote(s) for s in args]
    # Tried to use subprocess.run() with shell=False and shell=True and none work
    os.environ["SSHPASS"] = password
    result = os.system(" ".join(args_shlex))
    del os.environ['SSHPASS']
    #result = subprocess.run([ "sshpass", "-e", "ssh-copy-id", "-o", "StrictHostKeyChecking=no", user_and_machine, "-p", "2222" ], 
    #                        env={"SSHPASS":password}, check=True)
    return result
    