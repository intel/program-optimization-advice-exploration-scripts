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
import argparse
from sqlalchemy.orm import sessionmaker
from model_accessor import LoreMigrator
from qaas_database import QaaSDatabase
import os
import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from model import create_all_tables
import time  
import json
from util import get_config, connect_db

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read executions.csv in batches')
    parser.add_argument('--start', type=int,  help='Starting row to read from')
    parser.add_argument('--size', type=int,  help='Number of rows to read')
    parser.add_argument('--lore_csv_dir', type=str, default='/host/home/yjiao/lore_test', help='Path to the directory containing lore CSV files')

    args = parser.parse_args()


    # Connect to the database
    config = get_config()
    engine = create_all_tables(config, db="lore")
    Session = sessionmaker(bind=engine)
    session = Session()
    start_time = time.time()
    # Initialize LoreMigrator
    lore_csv_dir = args.lore_csv_dir
    migrator = LoreMigrator(session, lore_csv_dir)
    qaas_database = QaaSDatabase()
    qaas_database.accept(migrator)
    # Read executions in batch
    migrator.read_executions_in_batch(args.start, args.size)

    #save the orig loop map file 
    with open('orig_src_loop_map.json', 'wb') as f:
        json.dump(migrator.orig_src_loop_map, f)
    session.commit()
    session.close()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The script took {elapsed_time} seconds to run.")

    
