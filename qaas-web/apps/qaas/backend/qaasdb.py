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
from qaas_model_accessor import QaaSModelInitializer
from qaas_database import QaaSDatabase
#import pickle
from model import connect_db
from sqlalchemy.orm import sessionmaker
# populate database given the data in qaas data folder, gui timestamp is the timestamp for both opt and orig
def populate_database_qaas(report_path, config):
    #connect db
    engine = connect_db(config['web']['SQLALCHEMY_DATABASE_URI_QAAS'])
    Session = sessionmaker(bind=engine)
    session = Session()

    
    #######################populate database tables######################
    initializer = QaaSModelInitializer(session, report_path)
    qaas_database = QaaSDatabase()
    qaas_database.accept(initializer)
    
    session.commit()
    session.close()




