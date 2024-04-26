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
from flask import jsonify

def give_permission(folder, user):
    os.system(f"sudo chown -R {user}:{user} {folder}")
    os.system(f"sudo chmod -R 775 {folder}")

#save json after getting from frontend
def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return file_path

#get all json file
def get_all_jsons(input_json_dir):
    if not os.path.exists(input_json_dir):
        return []  
    
    filenames = os.listdir(input_json_dir)

    return {'filenames': filenames} 

#load json
def load_json(file_path):
    
    if not os.path.exists(file_path):
        return jsonify({"error": f"The file does not exist"}), 404
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    # data['application']['GIT']['TOKEN'] = '*' * len(data['application']['GIT']['TOKEN'])
    # data['application']['GIT']['DATA_TOKEN'] = '*' * len(data['application']['GIT']['TOKEN'])

    return jsonify(data)
