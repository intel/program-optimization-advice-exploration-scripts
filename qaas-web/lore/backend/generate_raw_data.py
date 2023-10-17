from flask import Flask,Response
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import pandas as pd
import subprocess
import json
import os
from model import * 
from util import *
import seaborn as sns
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time 
from sqlalchemy.orm import aliased
from sqlalchemy import asc
from functools import lru_cache
import pickle
import numpy as np
import pymysql
import time
lore_database_uri = 'mysql://qaas:qaas-password@localhost/lore'
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = lore_database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
def with_app_context(func):
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper

#this session is about getting raw data for first time


@lru_cache(maxsize=None)
def get_ref_from_loop(loop):
    return float(get_metrics_for_loop(loop)['novec'])

def get_key_from_src_loop(src_loop):
    if not src_loop:
        return None
    filename, function_name, line_number, mutation_number = extract_info_from_lore_source_code_file_name(src_loop.file)
    program = src_loop.execution.application.program
    return (program, filename, function_name, line_number)

@with_app_context
# for original loops
# DF1 = <source loop> *<representative source loop>* <mutation> *<compiler>* <time>
#   -- need to look at src table to figure out loops with same rep source loop
# for all loops (including original loops?)
# DF2 = <source loop> *<representative orig source loop>* <mutation>  *<compiler>* <time>
#  DF1.join(DF2, key=[<representative source loop>, <compiler>])
#
def get_all_mutations_time_per_orig_loop_per_compiler(compiler_vendor, compiler_version):
    #
    refs_per_orig_loop_key = {}

    loops = (db.session.query(Loop)
                         .join(Loop.compiler)
                         .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version)
                         .distinct().all())[:2000]
    
    print(len(loops))

    start_time = time.time()
    loop_count = 0
    for loop in loops:
        #get loop's src loop
        src_loop = loop.src_loop
        ref_value = get_ref_from_loop(loop)
        loop_key = get_key_from_src_loop(src_loop)
        loop_id = src_loop.table_id
        mutation_number = src_loop.mutation_number
        #if it is orig loop and it appear first time
        if mutation_number == 0 and loop_key not in refs_per_orig_loop_key:
            refs_per_orig_loop_key[loop_key] = [{f'{loop_id}_base' : ref_value}]
            continue


        #get its orig src loop
        orig_src_loop = src_loop.orig_src_loop
        orig_loop_key = get_key_from_src_loop(orig_src_loop)

        #loop showed up before its orig loop is added
        if orig_loop_key not in refs_per_orig_loop_key:
            #don't add the ref value because it might not be the correct compiler
            refs_per_orig_loop_key[orig_loop_key] = []

        #if it is orig loop it should be base value
        if mutation_number == 0:
            refs_per_orig_loop_key[orig_loop_key].append({f'{loop_id}_base' : ref_value})
        else:
            refs_per_orig_loop_key[orig_loop_key].append({loop_id : ref_value})
        loop_count += 1
        if loop_count % 1000 == 0:
            print(loop_count)


    print("total size", len(refs_per_orig_loop_key))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The entire compiler_version combination took {elapsed_time} seconds to run.")
    return refs_per_orig_loop_key



    


CHUNK_SIZE = 100
# @with_app_context
# def get_all_mutations_time_per_orig_loop_per_compiler(compiler_vendor, compiler_version):

#     #it will save the ref per orig loop, the index will represent the mutation number, the len is the mutaiton count
#     refs_per_orig_loop_key = {}
    
#     #load source loops in chunks into memory 
#     last_id = 0
#     iteration_number = 0
#     start_time1 = time.time()

#     while True:
#         start_time = time.time()
#         src_loops_chunk = (db.session.query(SrcLoop)
#                          .join(SrcLoop.loops)
#                          .join(Loop.compiler)
#                          .join(SrcLoop.execution)
#                          .join(Execution.application)
#                          .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version, SrcLoop.table_id > last_id)
#                          .order_by(Application.table_id, asc(SrcLoop.mutation_number), SrcLoop.table_id)
#                          .limit(CHUNK_SIZE)
#                          .all())
#         if not src_loops_chunk:
#             break
        
#         print(len(src_loops_chunk))
#         loop_count = 0
#         for src_loop in src_loops_chunk:
#             orig_filename, orig_function_name, orig_line_number, mutation_number = extract_info_from_lore_source_code_file_name(src_loop.file)
#             program = src_loop.execution.application.program

#             orig_loop_key = (program, orig_filename, orig_function_name, orig_line_number)

#             # get refs for each orig_loop_key
#             ref_value = get_ref_from_loop(src_loop.loops[0])
#             if orig_loop_key not in refs_per_orig_loop_key:
#                 refs_per_orig_loop_key[orig_loop_key] = []
#             refs_per_orig_loop_key[orig_loop_key].append(ref_value)
#             loop_count += 1
#             if loop_count % 1000 == 0:
#                 print(loop_count)

#         last_id = src_loops_chunk[-1].table_id
#         iteration_number += 1
#         print(last_id, iteration_number)
#         end_time = time.time()
#         elapsed_time = end_time - start_time
#         print(f"The entire iteration took {elapsed_time} seconds to run.")
#         # if iteration_number == 10:
            
#         #     break


#     raw_data = {
#         'refs_per_orig_loop_key': refs_per_orig_loop_key
#     }
#     end_time1 = time.time()

#     elapsed_time1 = end_time1 - start_time1
#     print(f"The entire compiler_version combination took {elapsed_time1} seconds to run.")
#     print("total size", len(raw_data['refs_per_orig_loop_key']))
#     return raw_data


#load and cache realtions functions
@with_app_context
def get_all_compiler_vendors_and_versions():
    return db.session.query(Compiler.vendor, Compiler.version).distinct().all()
    
cache_directory = os.path.join(os.getcwd(), 'cache')
#create dir for cache if not exist
if not os.path.exists(cache_directory):
    os.makedirs(cache_directory)



def cache_all_loops_raw_speedup_data_per_compiler(compiler_vendor, compiler_version):
    raw_data = get_all_mutations_time_per_orig_loop_per_compiler(compiler_vendor, compiler_version)
    cache_filename = os.path.join(cache_directory, f"all_mutations_time_per_orig_loop_{compiler_vendor}_{compiler_version}.pkl")
    with open(cache_filename, 'wb') as cache_file:
        pickle.dump(raw_data, cache_file)
    return raw_data

def create_cache_for_all_compiler_mutations_time_per_orig_loop():
    # compiler_vendors_and_versions = get_all_compiler_vendors_and_versions()
    compiler_vendors_and_versions = [('icc', '17.0.1')]
    for vendor, version in compiler_vendors_and_versions:
        cache_all_loops_raw_speedup_data_per_compiler(vendor, version)


    

if __name__ == '__main__':
    create_cache_for_all_compiler_mutations_time_per_orig_loop()

