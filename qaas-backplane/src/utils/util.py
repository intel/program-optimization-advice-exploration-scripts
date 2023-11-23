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
# Contributors: David/Hafid

import os
import subprocess
import datetime

# routine providing api usable for chaining
def make_dir(path):
    os.makedirs(path)
    return path

def generate_timestamp_str():
    return timestamp_str(generate_timestamp())

def generate_timestamp():
    return int(round(datetime.datetime.now().timestamp()))

def timestamp_str(locus_timestamp):
    locus_ts_str = str(locus_timestamp)
    locus_ts_str = locus_ts_str[:3] + "-" + locus_ts_str[3:6] + "-" + locus_ts_str[6:]
    return locus_ts_str


def split_compiler_combo(CC_combo):
    CC_combo = CC_combo.split("-")
    if len(CC_combo) == 1:
        mpi_wrapper = None
        CC = CC_combo[0]
    else:
        mpi_wrapper, CC = CC_combo
    return mpi_wrapper,CC

def load_compiler_env(compiler_dir):
    script = os.path.join(compiler_dir, 'Linux/intel64/load.sh')
    #script = '/nfs/site/proj/openmp/compilers/intel/19.0/Linux/intel64/load.sh'
    pipe = subprocess.Popen(f"/bin/bash -c 'source {script} --force && env'", stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    #for line in output.splitlines():
    #    print(str(line).split("=", 1))
    env = dict((line.split("=", 1) if '=' in line else ('','') for line in output.decode('utf-8').splitlines()))
    # try to pop the dummy '' key
    env.pop('','')
    return env


# parse the -var command line argument for env maps
def parse_env_map(args):
    return dict([(v.split("=",1)) for v in args.var]) if args.var else {}
