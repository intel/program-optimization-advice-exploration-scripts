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
import os
import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(current_directory, '../../common/backend/')))

from qaas_database import QaaSDatabase
from oneview_model_accessor import OneViewModelInitializerAndFileCopier, OneViewModelInitializer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from model import connect_db, create_all
from base_util import QaaSFileAccessMonitor, get_db_name_from_session, get_config

import argparse
def extract_ov_file(input_path, output_path, keep_db=False):
    with QaaSFileAccessMonitor(input_path, output_path, keep_db) as (session, large_files_folder):
        ######################populate database tables######################
        large_files_folder = os.path.join(large_files_folder, get_db_name_from_session(session))

        initializer = OneViewModelInitializer(session, input_path, "test_timestamp", "test_version", "workload_name", "workload_version_name", "workload_program_name", "workload_program_commit_id", large_files_folder)
        qaas_ov_database = QaaSDatabase()
        qaas_ov_database.accept(initializer)

def main():
    parser = argparse.ArgumentParser(description="OV data extractor")
    parser.add_argument('--input', help='input Oneview folder', required=True)
    parser.add_argument('--output', help='output Oneview folder', required=True)
    parser.add_argument('--keep-db', action='store_true', help='Keep the temporary database', required=False)
    args = parser.parse_args()
    #ov_path = "/host/localdisk/yue/data/test_qaas_ov_data/runs/170-335-6350/oneview_runs/defaults/orig/oneview_results_1703356350" # hardcoded now
    #output_path = "/tmp/test123"  #hardcoded now
    extract_ov_file(args.input, args.output, keep_db = args.keep_db)

if __name__ == "__main__":
    main()
