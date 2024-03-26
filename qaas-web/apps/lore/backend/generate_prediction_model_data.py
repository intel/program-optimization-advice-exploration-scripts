
from flask import Flask,Response
from flask import request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import pandas as pd
import json
import os
import sys
current_directory = os.getcwd()
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(1, base_directory)
from model import * 
from util import *
# %matplotlib widget
import seaborn as sns
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import time 
from sqlalchemy.orm import aliased
from sqlalchemy import asc
from functools import lru_cache
import json
import numpy as np
import pymysql
import configparser
from sqlalchemy import func, distinct
import psutil
config_path = os.path.join(current_directory, "../../config/qaas-web.conf")
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(config_path)
lore_database_uri = config['web']['SQLALCHEMY_DATABASE_URI_LORE']
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
#data cleanning
file_path = os.path.join(current_directory, 'compiler_prediction_model_data.csv')
from sklearn.preprocessing import MinMaxScaler
def calculate_rating(group):
    group['rating'] = group['base_median'].rank(method='min', ascending=True)
    group['rating'] = 1 / group['rating']

    return group

def add_metrics(metrics, loop_data):
    for metric in metrics:
        metric_value = metric.metric_value
        if metric.metric_value:
            try:
                float_metric_value = float(metric_value)
                loop_data[metric.metric_name] = float_metric_value

            except ValueError:
                continue
    
@with_app_context
def get_wanted_src_loops_csv():
    header_written = False
    
    #get all possible applications
    orig_src_loop_ids = db.session.query(SrcLoop.fk_orig_src_loop_id).filter(SrcLoop.orig_src_loop != None).distinct().all()
    #compiler used by each src loop
    count = 0
    for orig_src_loop_id_tuple in orig_src_loop_ids:
        data = []
        orig_src_loop_id = orig_src_loop_id_tuple[0]
        orig_src_loop = db.session.query(SrcLoop).filter_by(table_id = orig_src_loop_id).one()
        #mutations
        mutated_src_loops = db.session.query(SrcLoop).filter(SrcLoop.orig_src_loop == orig_src_loop).all()
        for mutated_src_loop in mutated_src_loops:
            compiler_info = mutated_src_loop.loops[0].compiler_option.compiler
            dynamic_measure = mutated_src_loop.loops[0].lore_loop_measures[0]
            dynamic_metrics = list(dynamic_measure.lore_loop_measure_metrics)
            static_metrics =  list(mutated_src_loop.source.source_metrics)
            
            loop_data = {
                'original_loop_id': orig_src_loop_id,
                'mutated_loop_id': mutated_src_loop.table_id,
                'mutation_number': mutated_src_loop.mutation_number,
                'compiler_vendor_version': f'{compiler_info.vendor}_{compiler_info.version}',
            }
            add_metrics(static_metrics, loop_data)
            add_metrics(dynamic_metrics, loop_data)
            data.append(loop_data)
            

        df = pd.DataFrame(data)
        #use df and find out what is the best cmpiler for each application
        df['is_best_compiler'] = 0
        for _, group in df.groupby('original_loop_id'):
            # row indwx with the min base_median
            best_compiler_idx = group['base_median'].idxmin()
            df.at[best_compiler_idx, 'is_best_compiler'] = 1
        df = df.groupby('original_loop_id', group_keys=False).apply(calculate_rating)
        with open(file_path, 'a', newline='') as f:
            df.to_csv(f, sep=',', index=False, header=not header_written)
            #only write header once
            if not header_written:
                header_written = True
        if count % 100 == 0:
            memory_usage = psutil.Process().memory_info().rss / (1024 ** 2)
            print(f"Memory usage: {memory_usage} MB")

get_wanted_src_loops_csv()