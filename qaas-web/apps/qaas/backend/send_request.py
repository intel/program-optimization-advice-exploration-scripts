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
from ovdb import populate_database, export_data
from lore_migrator import migrate_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
# Get the absolute path of the directory containing the qaas module
qaas_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'qaas-backplane', 'src'))

# Add the directory to sys.path
sys.path.append(qaas_dir)

# Now you can import the qaas module
import qaas
from server import app 
import configparser

from server import update_html, run_comparison_report
from model import create_all_tables
SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", "config", "qaas-web.conf")
#get the config
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
output_ov_dir = "/nfs/site/proj/alac/tmp/qaas-fix/tmp/qaas_data/167-80-123"
ov_output_dir = os.path.join(output_ov_dir,'oneview_runs')



# print the response
#test lore read
create_all_tables(config)
migrate_database()
#test ov data read and write
# for version in ['opt','orig']:
#     ov_version_output_dir = os.path.join(ov_output_dir, version)
#     result_folders = os.listdir(ov_version_output_dir)
#     # Should have only one folder
#     assert len(result_folders) == 1
#     result_folder = result_folders[0]
#     current_ov_dir = os.path.join(ov_version_output_dir, result_folder)
#     qaas_timestamp = os.path.basename(output_ov_dir)
#     workload_name = f"workload_name_{version}"
#     workload_version_name = f"version_name({version})"
#     workload_program_name = f"test_program_name_{version}"
#     workload_program_commit_id = f"test###id_{version}"
#     populate_database(current_ov_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
#     with app.app_context():
#         update_html(version)
    
# run_comparison_report()

#test export data
# def connect_db(config):
#     engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI_QAAS'])
#     engine.connect()
#     return engine
# engine = connect_db(config)
# Session = sessionmaker(bind=engine)
# session = Session()
# qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
# export_data('1681964819', qaas_output_folder, session)
# session.close()