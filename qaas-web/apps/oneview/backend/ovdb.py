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
from util import *
from model_accessor import OneViewModelInitializer,OneViewModelExporter
from qaas_database import QaaSDatabase
import pickle


# populate database given the data in qaas data folder, gui timestamp is the timestamp for both opt and orig
def populate_database(qaas_data_dir, qaas_timestamp, version, 
                      workload_name, workload_version_name, workload_program_name, workload_program_commit_id):
    #connect db
    config = get_config()
    engine = connect_db(config)
    Session = sessionmaker(bind=engine)
    session = Session()

    
    #######################populate database tables######################
    initializer = OneViewModelInitializer(session, qaas_data_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
    
    qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
    os.makedirs(qaas_output_folder, exist_ok=True)

    qaas_database = QaaSDatabase()
    qaas_database.accept(initializer)

    timestamp = qaas_database.universal_timestamp
  
    # export_data(timestamp, qaas_output_folder, session)
        
    session.commit()
    session.close()

def export_data(timestamp, qaas_output_folder, session):
    print("start find database", timestamp, qaas_output_folder)

    qaas_database = QaaSDatabase.find_database(timestamp, session)
    print("end find database", qaas_database)

    exporter = OneViewModelExporter(session, qaas_output_folder)
    print("start export data")
    qaas_database.export(exporter)
    print("finish export data")


