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
import json
input_json_dir = '/tmp/input_jsons'

#save json after getting from frontend
def save_json(data, filename):
    os.makedirs(input_json_dir, exist_ok=True)  # create directory if it doesn't exist
    file_path = os.path.join(input_json_dir, filename)
    
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

#get all json file
def get_all_jsons():
    if not os.path.exists(input_json_dir):
        return []  
    
    files = os.listdir(input_json_dir)
    json_data = {}
    for filename in files:
        data = load_json(input_json_dir, filename)
        json_data [filename] = data
    return json_data 

#load json
def load_json(input_json_dir, filename):
    file_path = os.path.join(input_json_dir, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {filename} does not exist in {input_json_dir}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data
