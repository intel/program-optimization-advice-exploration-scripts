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
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from oneview_model_accessor import OneViewModelExporter
from qaas_ov_model_accessor import QaaSOneViewModelInitializer
from qaas_ov_database import QaaSOneViewDatabase
from model import connect_db
from sqlalchemy.orm import sessionmaker

def populate_database_qaas_ov(report_path, config):
    #connect db
    engine = connect_db(config['web']['SQLALCHEMY_DATABASE_URI_QAAS_OV'])
    Session = sessionmaker(bind=engine)
    session = Session()

    
    #######################populate database tables######################
    initializer = QaaSOneViewModelInitializer(session, report_path, config['web']['LARGE_FILES_FOLDER'])
    qaas_ov_database = QaaSOneViewDatabase()
    qaas_ov_database.accept(initializer)
    
    session.commit()
    session.close()



def export_data(timestamp, qaas_output_folder, session):

    qaas_ov_database = QaaSOneViewDatabase.find_database(timestamp, session)
    exporter = OneViewModelExporter(session, qaas_output_folder)
    qaas_ov_database.export(exporter)

