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
import math
import json
import re
import luadata
import pandas as pd
import zlib
import hashlib
import struct
from datetime import datetime
import configparser
from sqlalchemy import distinct, func
from sqlalchemy.sql import and_
import csv
import numpy as np
import sys
from slpp import slpp as lua
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from model import *


SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", '..',"config", "qaas-web.conf")



#get the config
def get_config():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(CONFIG_PATH)
    return config

def connect_db(config):
    engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI_ONEVIEW'])
    engine.connect()
    return engine



#timestamp

##### parse file






####get files functions






        
def is_flag_in_compiler(flag, all_flags):
    if not all_flags:
        return 0
    return 1 if flag in all_flags else 0



##### convert file



##### compress/decompress file
def compress_file(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return zlib.compress(content, 9)

def get_file_sha256(filename):
    with open(filename, 'rb') as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()
    return sha256_hash
def decompress_file(compressed_content):
    return zlib.decompress(compressed_content)


####get file



#### create/write file


####### get obj from obj list



