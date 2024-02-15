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
# Created April 2023
# Contributors: Hafid/David

from argparse import ArgumentParser
import subprocess
import os
import sys
import csv
import numpy as np

import app_builder
import app_runner
import lprof_runner
import oneview_runner
from logger import log, QaasComponents
from wrapper_runner import compiler_run
import configparser

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))

DEFAULT_REPETITIONS = 3

def dump_compilers_log_file(qaas_reports_dir, file_name, message):
    '''Dump compare compilers runs log'''

    f_compiler = open(os.path.join(qaas_reports_dir, file_name), "w")
    f_compiler.write(message)
    f_compiler.close()

def set_compilers_csv_header(defaults):
    '''Set CSV header for compiler runs'''
    csv_header = ['app_name', 'compiler', 'option #', 'flags', '#MPI', '#OMP', 'time(s)', 'GFlops/s']
    for default in defaults:
        csv_header.append(f"Spd w.r.t {default}")
    return csv_header

def dump_compilers_csv_file(qaas_reports_dir, file_name, table, defaults, best_only=False, best_options=None):
    '''Dump Compilers runs to csv'''

    # Check file exist status
    file_exists = True if os.path.isfile(os.path.join(qaas_reports_dir, file_name)) else False
    # Open the csv file in append mode
    csv_compiler = open(os.path.join(qaas_reports_dir, file_name), "a", newline='\n')
    writer = csv.writer(csv_compiler)
    # Do not add header if file exists already
    if not file_exists:
        writer.writerow(set_compilers_csv_header(defaults))

    # Write execution times to csv format
    for compiler in table:
        if not best_only:
            writer.writerows(table[compiler])
        else:
            writer.writerow(table[compiler][best_options[compiler]])
    csv_compiler.close()

def find_best_compiler(table, best_opt, i_time):
    '''Find best compiler across QaaS options'''

    bestcomp = None
    min_time = 0.0
    for compiler,best_opt in best_opt.items():
        time = table[compiler][best_opt][i_time]
        if time == None:
            continue
        if min_time == 0.0 or time < min_time:
            min_time = time
            bestcomp = compiler

    return bestcomp

def compute_compilers_speedups(t_compilers, defaults, i_time):
    '''Compute Speedups w/r original and different compiler defaults'''

    for compiler in t_compilers:
        for row  in t_compilers[compiler]:
            for item in defaults:
                if row[i_time] != None and defaults[item] != None:
                    # Compare to user provided compiler and flags
                    row.append(float(defaults[item])/float(row[i_time]))
                    #row.append(float(t_unicore[list(t_unicore.keys())[0]][0][i_time])/float(row[i_time]))
                else:
                    # Compare to
                    row.append(0.0)

def measure_exec_times(app_name, base_run_dir, data_dir, run_cmd, compiled_options, maqao_dir, flops, parallel_runs):
    '''Measure Application-wide execution times'''

    # Add extra OV runs
    ov_run_dir_root = os.path.join(os.path.dirname(base_run_dir), 'other_ov_runs')
    os.makedirs(ov_run_dir_root, exist_ok=True)
    # Compare options
    run_log=""
    qaas_best_opt = dict()
    qaas_table = dict()
    for compiler in compiled_options:
        time_values = []
        t_compiler = []
        for binary_path,app_env,flags in compiled_options[compiler]:
            # Extract tested configuration
            _,option = os.path.basename(os.path.dirname(binary_path)).split('_')
            # Setup run directory and launch initial run
            base_run_bin_dir = os.path.join(base_run_dir, 'compilers', f"{compiler}_{option}")
            basic_run,nb_mpi,nb_omp = compiler_run(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd,
                                                   DEFAULT_REPETITIONS, "app", parallel_runs)
            tmp = [str(x) for x in basic_run.exec_times]
            # Check execution in defined range
            median_value = basic_run.compute_median_exec_time()
            run_log += f"[Compiler Options] (compiler={compiler},option={option}) Median on {DEFAULT_REPETITIONS} runs: {median_value}\n"
            time_values.append(median_value)
            gflops = flops/float(median_value) if median_value != None else 0.0
            t_compiler.append([app_name, compiler, option, flags,nb_mpi,nb_omp, median_value, gflops])

        # Add the local table to dict
        qaas_table[compiler] = t_compiler
        # Find best option for current compiler
        time_values = np.array([x if x != None else 10000  for x in time_values])
        qaas_min_val = time_values.min()
        qaas_best_opt[compiler] = time_values.argmin()
        qaas_min_opt =  qaas_best_opt[compiler] + 1  # option indexing starts at 1.
        run_log += f"[Compiler Options] Fastest compilation {compiler} variant is {qaas_min_opt} with {qaas_min_val} seconds\n"


    return (qaas_table, qaas_best_opt, run_log)

def run_ov_on_best(ov_run_dir, ov_config, maqao_dir, data_dir, run_cmd, qaas_best_opt, compiled_options, parallel_runs):
    '''Run and generate OneView reports on best options'''

    for compiler, best_opt in qaas_best_opt.items():
        # keep option directories consistent with build naming convention
        option = best_opt + 1
        # Setup experiment directory on oneview run directory
        ov_run_dir_opt = os.path.join(ov_run_dir, "compilers", f"{compiler}_{option}")
        # Extract the binary path of the best option
        binary_path = compiled_options[compiler][best_opt][0]
        # Retrieve the execution environment
        app_env = compiled_options[compiler][best_opt][1]
        # Make the oneview run
        compiler_run(app_env, binary_path, data_dir, ov_run_dir_opt, run_cmd, DEFAULT_REPETITIONS, "oneview", parallel_runs, maqao_dir, ov_config)

def run_qaas_UP(app_name, src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                orig_user_CC, run_cmd, compiled_options, qaas_reports_dir, defaults, flops, parallel_runs):
    '''Execute QAAS Running Logic: UNICORE PARAMETER EXPLORATION/TUNING'''

    # Init status
    rc=0
    # Compare options
    qaas_table, qaas_best_opt, log = measure_exec_times(app_name, base_run_dir, data_dir, run_cmd, compiled_options, maqao_dir, flops, parallel_runs)

    # Print log to file
    dump_compilers_log_file(qaas_reports_dir, 'qaas_compilers.log', log)

    # Compute speedups
    index = 6 # index of the median execution time column
    compute_compilers_speedups(qaas_table, defaults, index)

    # Dump csv table to file
    dump_compilers_csv_file(qaas_reports_dir, 'qaas_compilers.csv', qaas_table, defaults)
    # Dump best options csv file
    dump_compilers_csv_file(qaas_reports_dir, 'qaas_compilers_best.csv', qaas_table, defaults, True, qaas_best_opt)

    # Dump meta data file
    meta_config = configparser.ConfigParser()
    meta_config['qaas'] = { "run_cmd": f'"{run_cmd}"' }
    with open(os.path.join(qaas_reports_dir, 'input.txt'), 'w') as meta_config_file:
        meta_config.write(meta_config_file)

    # Run oneview on best options
    run_ov_on_best(ov_run_dir, ov_config, maqao_dir, data_dir, run_cmd, qaas_best_opt, compiled_options, parallel_runs)

    # Find best compiler
    qaas_best_comp = find_best_compiler(qaas_table, qaas_best_opt, index)

    return rc,qaas_best_opt,qaas_best_comp,""
