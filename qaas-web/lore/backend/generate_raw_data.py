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
import psutil
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
#load and cache realtions functions
@with_app_context
def get_all_compiler_vendors_and_versions():
    return db.session.query(Compiler.vendor, Compiler.version).distinct().all()
    
cache_directory = os.path.join(os.getcwd(), 'cache')
#create dir for cache if not exist
if not os.path.exists(cache_directory):
    os.makedirs(cache_directory)

def get_ref_from_loop(loop):
    metrics = loop.lore_loop_measures[0].lore_loop_measure_metrics
    novec_value = None
    for metric in metrics:
        if metric.metric_name == 'novec_median':
            novec_value = float(metric.metric_value)
            break

    return novec_value


@with_app_context
def get_all_mutations_time_per_orig_loop_per_compiler(compiler_vendor, compiler_version):
    db.session.expunge_all()
    BATCH_SIZE = 5000
    cache_filename = os.path.join(cache_directory, f"all_mutations_time_per_orig_loop_{compiler_vendor}_{compiler_version}.pkl")
    if os.path.exists(cache_filename):
        os.remove(cache_filename)
    count = 0
    
    
    loop_count = (db.session.query(Loop)
             .join(Loop.compiler)
             .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version)
             .distinct().count())

    
    # Process loops in batches
    for i in range(0, loop_count, BATCH_SIZE):
        #load the batch file
        if os.path.exists(cache_filename):
            with open(cache_filename, 'rb') as cache_file:
                refs_per_source = pickle.load(cache_file)
        else:
            refs_per_source = {}
        db.session.expunge_all()

        batch_loops = (db.session.query(Loop)
                       .join(Loop.compiler)
                       .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version)
                       .slice(i, i + BATCH_SIZE).distinct().all())
        
        for loop in batch_loops:
            # loop's src loop
            src_loop = loop.src_loop  
            ref_value = get_ref_from_loop(loop)
            mutation_number = src_loop.mutation_number
            orig_src_loop = src_loop.orig_src_loop
            source_id = src_loop.source.table_id if not orig_src_loop else orig_src_loop.source.table_id
            refs_per_source.setdefault(source_id, []).append({mutation_number: ref_value})

            count += 1

            if count % 1000 == 0:
                print(f"Batch count: {count}")
                memory_usage = psutil.Process().memory_info().rss / (1024 ** 2)
                print(f"Memory usage: {memory_usage} MB")
                
          # Save to cache
        with open(cache_filename, 'wb') as cache_file:
            pickle.dump(refs_per_source, cache_file)
            
    
    return refs_per_source

# for original loops
# DF1 = <source loop> *<representative source loop>* <mutation> *<compiler>* <time>
#   -- need to look at src table to figure out loops with same rep source loop
# for all loops (including original loops?)
# DF2 = <source loop> *<representative orig source loop>* <mutation>  *<compiler>* <time>
#  DF1.join(DF2, key=[<representative source loop>, <compiler>])
#
# def get_all_mutations_time_per_orig_loop_per_compiler(compiler_vendor, compiler_version):
#     #
#     refs_per_source = {}

#     loops = (db.session.query(Loop)
#                          .join(Loop.compiler)
#                          .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version)
#                          .distinct().all())[:2000]

    
#     print(len(loops))
#     BATCH_SIZE = 5000

#     start_time = time.time()
#     loop_count = 0
#     for loop in loops:
#         #get loop's src loop
#         src_loop = loop.src_loop
#         ref_value = get_ref_from_loop(loop)
#         mutation_number = src_loop.mutation_number
            
#         #get its orig src loop
#         orig_src_loop = src_loop.orig_src_loop
#         #default to be orig loop i.e. mutation = 0
#         source_id = src_loop.source.table_id
#         if orig_src_loop:
#             source_id = orig_src_loop.source.table_id

#         #loop showed up before its orig loop is added
#         if source_id not in refs_per_source:
#             #don't add the ref value because it might not be the correct compiler
#             refs_per_source[source_id] = []

       
#         refs_per_source[source_id].append({mutation_number : ref_value})
#         loop_count += 1
#         if loop_count % 1000 == 0:
#             memory_usage = psutil.Process().memory_info().rss / (1024 ** 2)  # RSS value converted to MB
#             print(f"Memory usage: {memory_usage} MB")


#     print("total size", len(refs_per_source))
#     # end_time = time.time()
#     # elapsed_time = end_time - start_time
#     # print(f"The entire compiler_version combination took {elapsed_time} seconds to run.")
#     return refs_per_source

def create_cache_for_all_compiler_mutations_time_per_orig_loop():
    # compiler_vendors_and_versions = get_all_compiler_vendors_and_versions()
    compiler_vendors_and_versions = [('icc', '17.0.1')]
    for vendor, version in compiler_vendors_and_versions:
        get_all_mutations_time_per_orig_loop_per_compiler(vendor, version)


    

if __name__ == '__main__':
    create_cache_for_all_compiler_mutations_time_per_orig_loop()

