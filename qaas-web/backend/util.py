import os
import math
import json
import re
import luadata
import pandas as pd
import zlib
import hashlib
import struct
from model import *
from datetime import datetime
import configparser
from sqlalchemy import distinct, func
from sqlalchemy.sql import and_
import csv
import numpy as np
level_map = {0: 'Single', 1: 'Innermost', 2: 'InBetween', 3: 'Outermost'}
reverse_level_map = {v: k for k, v in level_map.items()}

SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", "config", "qaas-web.conf")

def safe_division(n, d):
    if n is None or d is None:
        return None
    return n / d

#get the config
def get_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config

def connect_db(config):
    engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI'])
    engine.connect()
    return engine



#timestamp
def universal_timestamp_to_datetime(universal_timestamp):
    return datetime.fromtimestamp(int(universal_timestamp)).strftime("%c")

def datetime_to_universal_timestamp(date_time):
    return str(int(datetime.strptime(date_time, '%c').timestamp()))
##### parse file
def parse_file_name_no_variant(file_name):
    match = re.match(r'^(?:(fct)_)?(\w+)_(\d+)(?:(_cqa))?(?:(_text))?(?:(\.csv))?(?:(\.txt))?(?:(\.lua))?$', file_name)
    if match:
        module = match.group(2)
        identifier = match.group(3)
        type = 1 if "fct" in file_name else 0
        return type, module, identifier
    else:
        return None

def parse_file_name(file_name):
    match = re.match(r'^(?:(fct)_)?(?:([A-Z0-9]+)_)?(.*?_(\d+))(?:_cqa)?(?:_text)?(?:\.csv)?(?:\.txt)?(?:\.lua)?$', file_name)
    if match:
        fct = match.group(1)
        variant = match.group(2)
        module_and_id = match.group(3)
        # Separate module and id from the combined string
        module, identifier = module_and_id.rsplit('_', 1)
        type = 1 if fct is not None else 0
        return type, variant, module, identifier
    else:
        return None

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


def combine_source_info(source_name, line_number):
    if not source_name and not line_number:
        return None
    source_files = source_name.split(',')
    line_numbers = line_number.split(',')

    if len(source_files) != len(line_numbers):
        raise ValueError("The number of source files must match the number of line numbers.")

    combined = [f'{file.strip()}:{line.strip()}' for file, line in zip(source_files, line_numbers)]
    
    return ','.join(combined)

####get files functions
def get_files_with_extension(directory, extensions):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(tuple(extensions)) :
            files.append(os.path.join(directory, filename))
    return files

def get_files_starting_with_and_ending_with(directory, prefix, suffix):
    files = os.listdir(directory)
    filtered_files = [os.path.join(directory, file) for file in files if file.startswith(prefix) and file.endswith(suffix)]
    return filtered_files

def get_files_with_pattern(directory, pattern):
    files = []
    for file in os.listdir(directory):
        match = re.match(pattern, file)
        if match:
            files.append(file)
    
    return files

def is_df_empty(df):
    return df.applymap(lambda x: x is None).all().all()
        

def read_file(path, delimiter=';'):
    df = pd.read_csv(path, sep=delimiter, keep_default_na=False, index_col=False, skipinitialspace=True, na_values=[''])
    df = df.replace({np.nan: None})
    return df

def get_value(dic, key, type):
    value = dic.get(key, None)
    return type(value) if value is not None else None

def write_file(df, path, delimiter=';'):
    df.to_csv(path, sep=delimiter, index=False, header=True)

def get_or_create_df(path):
    if os.path.exists(path):
        df = read_file(path)
    else:
        df = pd.DataFrame()
    return df

def create_or_update_localvar_df(metric, value, file_path):
    try:
        df = pd.read_csv(file_path, sep=';', index_col=None)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['metric', 'value'])

 
    new_data = pd.DataFrame({'metric': [metric], 'value': [value]})
    df = pd.concat([df, new_data], ignore_index=True)

    df.to_csv(file_path, sep=';', index=False)

##### convert file

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

def add_commas_inside_brackets(lua_code):
    result = ''
    bracket_count = 0

    for i, char in enumerate(lua_code):
        if char == '{':
            bracket_count += 1
            result += char
        elif char == '}':
            bracket_count -= 1
            result += char
        elif char == '\n' and bracket_count > 0 and lua_code[i-1] != '{':
            result += ','
            result += char
        else:
            result += char

    return result

def convert_python_to_lua(python_object,lua_file_path):
    with open(lua_file_path, 'wb') as f:
        f.write(decompress_file(python_object))
    #TODO use json instead of string
    # lua_code = luadata.serialize(python_object, encoding="utf-8", indent="")
    # lua_code = lua_code[1:-1]  
    # lua_code = lua_code.replace('\\\\', '\\')
    # lua_code = lua_code.lstrip()
    # lua_code = lua_code.replace(',', '')
    # lua_code = add_commas_inside_brackets(lua_code)

    # with open(lua_file_path, 'w', encoding="utf-8") as f:
    #     f.write(lua_code)


def file_is_lua_table(lua_code):
    pattern = r'^\s*\w+\s*=\s*\{[\s\S]*\}\s*$'
    
    # check if the Lua code string matches the pattern
    return bool(re.match(pattern, lua_code))
def parse_line(content):
    line = None
    try:
        line = next(content).strip()
        while line.startswith("--"):
            line = next(content).strip()
    except StopIteration:
        pass
    return line

def process_value(value, content):
    if value == "nil":
        return None
    elif value.isdigit():
        return int(value)
    elif value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    elif value == "true":
        return True
    elif value == "false":
        return False
    elif value.startswith("{"):
        
        return parse_dict(content)
    return value

def parse_dict(content):
    value_dict = {}
    line = parse_line(content)
    if line and line.startswith("}"):
        return value_dict
    while line and not line.startswith("}"):
        if "=" in line:
            inner_key, inner_value = line.split("=", 1)
            inner_key, inner_value = inner_key.strip(), inner_value.strip()
            value_dict[inner_key] = process_value(inner_value, content)
        line = parse_line(content)
    return value_dict

def convert_non_table_lua_to_python(lua_file):
    with open(lua_file, 'r', encoding="utf-8") as f:
        content = iter(f.readlines())

    config = {}
    line = parse_line(content)
    while line:
        if "=" in line:
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            config[key] = process_value(value, content)
        line = parse_line(content)

    return config
def convert_lua_to_python(lua_file):
    if os.path.exists(lua_file):
        return compress_file(lua_file)
    #TODO use json instead of string
    # with open(lua_file, 'r', encoding="utf-8") as f:
    #     lua_code = f.read()

    # if not file_is_lua_table(lua_code):
    #     with open(lua_file, 'r') as file:
    #         lua_string = file.read()
    #         return lua_string
    # else:
    #     # Wrap the Lua code in a table
    #     wrapped_lua_code = "return {" + lua_code + "}"

    #     python_object = luadata.unserialize(wrapped_lua_code)

    #     # Extract the outermost dictionary
    #     return python_object



##### compress/decompress file
def compress_file(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return zlib.compress(content, 9)

def get_file_sha256(filename):
    with open(filename, 'rb') as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()
    return sha256_hash
def decompress_file(compressed_content):
    return zlib.decompress(compressed_content)


####get file
def get_data_from_csv(csv_path):
    num_cols = len(open(csv_path).readline().split(';'))
    if num_cols <= 1:
        return None
    data = pd.read_csv(csv_path,sep=';',index_col=None,skipinitialspace=True,usecols=range(num_cols - 1)).to_dict(orient='records')
    return data


#### create/write file
def write_dict_to_file(my_dict, filename):
    with open(filename, "w") as f:
        for key, value in my_dict.items():
            # If the value contains newline characters, replace them with "\n"
            value = value[0].replace("\n", "\\n")
            # Write the key-value pair to the file
            f.write(f"{key}={value}\n")

def get_names_and_values_data_for_metric_table(metrics):
    data = {}
    for metric in metrics:
        data[metric.metric_name] = metric.metric_value 
    return data


def text_to_list(text):
    html = ['<ul>']
    for line in text.split('\n'):
        li_content = line[2:]
        html.append(f'<li>{li_content}</li>')
    html.append('</ul>')
    return ''.join(html)

def text_to_table(text):
    sections = text.split('\n\n')
    html = []

    for section in sections:
        lines = section.split('\n')
        section_title = lines[0]
        html.append(f'<p>{section_title}</p>')
        html.append('<table>')

        for line in lines[1:]:
            key, value = line.split(':', 1)
            html.append(f'<tr><td>{key.strip()}</td><td>{value.strip()}</td></tr>')

        html.append('</table>')

    return ''.join(html)

def process_nested_dict(input_dict):
    output_dict = {}

    def apply_text_to_list(value):
        if '-' in value:
            return text_to_list(value)
        else:
            return value

    def process_item(item):
        if isinstance(item, dict):
            processed_item = {}
            for sub_key, sub_value in item.items():
                if sub_key in ['workaround', 'details']:
                    processed_item[sub_key] = apply_text_to_list(sub_value)
                elif sub_key == 'txt':
                    if 'expert' in item:
                        processed_item[sub_key] = text_to_table(sub_value)
                    else:
                        processed_item[sub_key] = sub_value
                else:
                    processed_item[sub_key] = sub_value
            return processed_item
        else:
            return item

    for key, value in input_dict.items():
        if isinstance(value, dict):
            output_dict[key] = process_nested_dict(value)
        elif isinstance(value, list):
            output_dict[key] = [process_item(item) for item in value]
        else:
            output_dict[key] = value

    return output_dict

def create_html_lua_by_text_python(analysis_python_data, analysis_html_lua_path):
    convert_python_to_lua(analysis_python_data,analysis_html_lua_path)

    #TODO change to process instead of just writeing the same data
    # output_dict = process_nested_dict(analysis_python_data)
    # convert_python_to_lua(output_dict,analysis_html_lua_path)






####### get obj from obj list
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
def get_loop_by_source_loop(src_loop, loops):
    res = None
    for loop in loops:
        if loop.src_loop == src_loop:
            return loop
    return res

def get_all_loops_from_src_loops(src_loops):
    loops = []
    for src_loop in src_loops:
        loops.extend(src_loop.loops)
    unique_loops = list(set(loops))
    return unique_loops

def get_all_functions_from_src_functions(src_functions):
    functions = []
    for src_function in src_functions:
        functions.extend(src_function.functions)
    unique_functions = list(set(functions))
    return unique_functions
def get_function_by_source_function(src_function, functions):
    res = None
    for function in functions:
        if function.src_function == src_function:
            return function
    return res

def get_block(blocks, block_id,pid, tid):
    res = None
    for block in  blocks:
        if block.maqao_block_id == block_id and block.pid == pid and block.tid == tid:
            return block
    return res
def get_obj_by_tid_and_pid(objs, pid, tid):
    res = []
    for obj in objs:
        if obj.pid == pid and obj.tid == tid:
            res.append(obj)
    return res
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

def get_all_functions(loop_collection):
    all_loops = loop_collection.get_objs()
    function_set = set()
    for loop in all_loops:
        function_set.add(loop.function)
    return function_set

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
        if function.asm:
            res.append(function.asm)
    for loop in loops:
        if loop.asm:
            res.append(loop.asm)
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


###### lore get data
def get_metric_value(src_metrics, target_metric_name):
    for src_metric in src_metrics:
        metric_name = src_metric.metric_name
        metric_value = src_metric.metric_value

        if metric_name == target_metric_name:
            return metric_value

    # Return the default value if the target metric is not found
    return None

def delete_data_from_dict(dict_data, to_del):
    for column in to_del:
        if column in dict_data:
            del dict_data[column]
    return dict_data

def count_mutations_for_orig_src_loop_id(session, orig_src_loop_id):
    # Count the number of distinct fk_mutation_id values for the specified orig_src_loop_id
    mutation_count = session.query(func.count(distinct(SrcLoop.fk_mutation_id))) \
                            .join(Mutation, SrcLoop.fk_mutation_id == Mutation.table_id) \
                            .filter(and_(SrcLoop.fk_orig_src_loop_id == orig_src_loop_id,
                                         Mutation.mutation_number != -1)) \
                            .scalar()
    return mutation_count

def count_loops_for_application(application):
    executions = application.executions
    count = 0
    for execution in executions:
        count += len(execution.src_loops)
    return count
#########

###### df and dict opreations
def get_columns(table):
    return [column.name for column in table.__table__.columns if not column.primary_key and not column.foreign_keys]

def get_extra_columns(table):
    return [column.name for column in table.__table__.columns if column.primary_key or column.foreign_keys ]


def delete_nan_from_dict(dict):
    return {k: v for k, v in dict.items() if not (isinstance(v, float) and math.isnan(v))}

def get_table_data_from_df(df, Table):
    columns = get_columns(Table)
    data = df.reindex(columns, axis=1).to_dict(orient='records')
    
    # Remove nan values from each dictionary
    cleaned_data = [delete_nan_from_dict(record) for record in data]
    
    return cleaned_data

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


def add_dict_to_df(dict_to_append, df):        
    df_to_append = pd.DataFrame(dict_to_append, index=[0])
    df = pd.concat([df, df_to_append], ignore_index=True)
    return df



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

###### binary file reading functions
def read_int(file):
    data = file.read(4)
    if len(data) != 4:
        raise IOError("Unexpected end of file")
    return struct.unpack("<i", data)[0]
def read_double(file):
    data = file.read(8)
    if len(data) != 8:
        raise IOError("Unexpected end of file")
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
    # Read the source file section of the object.
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

def read_objects(objects_count, f, strings, session):
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
    if not os.path.exists(binary_file_path): return None
    with open(binary_file_path, 'rb') as f:
        headers = read_header(f)
        # Read the first section of the file, which contains strings.
        strings_count = read_int(f)
        strings = read_dictionary(strings_count, f, session)

        # Read the second section of the file, which contains objects.
        objects_count = read_int(f)
        objects = read_objects(objects_count, f, strings, session)

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

def write_objects(f, objects, session):
    write_int(f, len(objects))

    for obj in objects:
        write_int(f, obj['module'])
        write_int(f, obj['identifier'])
        write_int(f, obj['compilation_options'])
        write_int(f, obj['source_file'])
        write_int(f, obj['start_line'])
        write_int(f, obj['stop_line'])
        write_source_file_intervals(f, obj['source_file_intervals'], session)
        


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
    if os.path.exists(binary_file_path):
        with open(binary_file_path, 'wb') as f:
            write_header(f, data['headers'],'OV_SRCLO')
            strings, objects = map_and_write_strings_location(f, data['objects'], session)
            write_strings(f, strings)
            write_objects(f, objects, session)

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
    if not os.path.exists(binary_file_path): return None

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
    if os.path.exists(binary_file_path):

        with open(binary_file_path, 'wb') as f:
            write_header(f, data['headers'], "OV_CALLC")
            strings, objects = map_and_write_strings_callchain(f, data['callchains'], session)
            write_strings(f, strings)
            write_callchains(f, objects)
