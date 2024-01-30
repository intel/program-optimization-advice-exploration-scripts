#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# MIT License

# Copyright (c) 2023 Intel-Sandbox
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# HISTORY
# Created October 2022
# Contributors: Yue/David
from flask import Flask,Response
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import pandas as pd
import subprocess
import json
import os
import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from model import * 
from util import *
import pandas as pd
import time 
from sqlalchemy.orm import aliased
from sqlalchemy import asc
from functools import lru_cache
# import pickle
import numpy as np
import pymysql
import time
import psutil
import configparser
import json
script_dir=os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "../../config/qaas-web.conf")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_path)
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config['web']['SQLALCHEMY_DATABASE_URI_LORE']
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


@with_app_context
def get_all_mutations_time_per_orig_loop_per_compiler(compiler_vendor, compiler_version):
    db.session.expunge_all()
    BATCH_SIZE = 5000
    # cache_filename = os.path.join(cache_directory, f"all_mutations_time_per_orig_loop_{compiler_vendor}_{compiler_version}.pkl")
    cache_filename = os.path.join(cache_directory, f"all_mutations_time_per_orig_loop_{compiler_vendor}_{compiler_version}.json")

    if os.path.exists(cache_filename):
        os.remove(cache_filename)
    count = 0
    
    
    loop_count = (db.session.query(Loop)
             .join(Loop.compiler_option)
             .join(CompilerOption.compiler)
             .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version)
             .distinct().count())

    print("total count",loop_count)
    
    # Process loops in batches
    # for i in range(0, loop_count, BATCH_SIZE):
    for i in range(0, loop_count, BATCH_SIZE):

        #load the batch file
        if os.path.exists(cache_filename):
            with open(cache_filename, 'rb') as cache_file:
                # refs_per_orig_src_loop = pickle.load(cache_file)
                refs_per_orig_src_loop = json.load(cache_file)

        else:
            refs_per_orig_src_loop = {}
        db.session.expunge_all()

        batch_loops = (db.session.query(Loop)
                       .join(Loop.compiler_option)
                       .join(CompilerOption.compiler)
                       .filter(Compiler.vendor == compiler_vendor, Compiler.version == compiler_version)
                       .slice(i, i + BATCH_SIZE).distinct().all())
        print("batch_loops",len(batch_loops))

        for loop in batch_loops:
            # loop's src loop
            src_loop = loop.src_loop  
            ref_value =(db.session.query(LoreLoopMeasureMetric)
             .filter_by(metric_name = "base_median", lore_loop_measure = loop.lore_loop_measures[0]).first().metric_value)
            hwcounter_value = (db.session.query(LoreLoopMeasureMetric)
             .filter_by(metric_name = "base_CPU_CLK_UNHALTED_THREAD", lore_loop_measure = loop.lore_loop_measures[0]).first().metric_value)
                    
            loop_data = {
                'base_median' : ref_value,
                'base_CPU_CLK_UNHALTED_THREAD' : hwcounter_value
            }

            orig_src_loop = src_loop.orig_src_loop
            #is orig src loop with target compiler
            oirg_src_loop_id = src_loop.table_id 
            #has orig src loop 
            if orig_src_loop:
                orig_loop_compiler = orig_src_loop.loops[0].compiler_option.compiler
                if orig_loop_compiler.vendor == compiler_vendor and orig_loop_compiler.version == compiler_version:
                    #same compiler
                     oirg_src_loop_id = orig_src_loop.table_id
                else:
                    #different compiler, get the src loop that has same source and program
                    orig_src_loop_same_compiler = (db.session.query(SrcLoop)
                                                    .join(Loop.src_loop)
                                                    .join(Loop.compiler_option)
                                                    .join(CompilerOption.compiler)
                                                    .join(SrcLoop.execution)
                                                    .join(Execution.application)
                                                    .filter(Compiler.vendor == compiler_vendor,
                                                            Compiler.version == compiler_version, 
                                                            SrcLoop.source == orig_src_loop.source,
                                                            Application.program == orig_src_loop.execution.application.program,
                                                            Application.workload == orig_src_loop.execution.application.workload,
                                                            SrcLoop.file == orig_src_loop.file,
                                                            SrcLoop.line_number == orig_src_loop.line_number)
                                                    .one())
                    oirg_src_loop_id = orig_src_loop_same_compiler.table_id


            #find out what is the correct src loop id 
            refs_per_orig_src_loop.setdefault(oirg_src_loop_id, []).append({src_loop.table_id: loop_data})

            count += 1

            if count % 1000 == 0:
                print(f"Batch count: {count}")
                memory_usage = psutil.Process().memory_info().rss / (1024 ** 2)
                print(f"Memory usage: {memory_usage} MB")
                
          # Save to cache
        with open(cache_filename, 'wb') as cache_file:
            # pickle.dump(refs_per_orig_src_loop, cache_file)
            json.dump(refs_per_orig_src_loop, cache_file)

            
    
    return refs_per_orig_src_loop


def create_cache_for_all_compiler_mutations_time_per_orig_loop():
    # compiler_vendors_and_versions = get_all_compiler_vendors_and_versions()
    compiler_vendors_and_versions = [('icc', '17.0.1')]
    # compiler_vendors_and_versions = [('gcc','6.2.0')]
    # compiler_vendors_and_versions = [('clang','4.0.0')]

    #('icc', '17.0.1'),('icc','15.0.6'),('gcc','6.2.0'),('gcc','4.8.5'),('gcc','4.7.4'),('clang','4.0.0'),('clang','3.6.2'),('clang','3.4.2')
    for vendor, version in compiler_vendors_and_versions:
        get_all_mutations_time_per_orig_loop_per_compiler(vendor, version)


    

if __name__ == '__main__':
    create_cache_for_all_compiler_mutations_time_per_orig_loop()

