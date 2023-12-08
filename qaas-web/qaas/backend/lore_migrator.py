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

from model import *

from model_accessor import LoreMigrator
from qaas_database import QaaSDatabase
from util import get_config, connect_db 


# populate database given the data in qaas data folder, gui timestamp is the timestamp for both opt and orig
def migrate_database():
    lore_csv_dir = '/nfs/site/proj/alac/members/yue/lore_test'
    #connect db
    config = get_config()
    engine = connect_db(config)
    Session = sessionmaker(bind=engine)
    session = Session()

    
    #######################populate database tables######################
    initializer = LoreMigrator(session, lore_csv_dir)

    qaas_database = QaaSDatabase()
    qaas_database.accept(initializer)
  
        
    session.commit()
    session.close()



