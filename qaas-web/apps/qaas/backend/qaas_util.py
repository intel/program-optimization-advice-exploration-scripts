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
import pandas as pd
import configparser
SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", '..',"config", "qaas-web.conf")
#get the config
def get_config():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(CONFIG_PATH)
    return config

def connect_db(config):
    engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI_QAAS'])
    engine.connect()
    return engine

#used to read the qaas metadata file
def parse_text_to_dict(file_path):
    data_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            # split by =
            parts = line.strip().split('=')
            if len(parts) == 2:
                key, value = parts
                data_dict[key] = value
    return data_dict
