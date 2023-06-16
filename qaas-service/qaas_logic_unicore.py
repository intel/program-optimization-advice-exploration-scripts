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

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))

DEFAULT_REPETITIONS = 3

def dump_unicore_log_file(qaas_reports_dir, file_name, message):
    '''Dump unicore runs log'''

    f_unicore = open(os.path.join(qaas_reports_dir, file_name), "w")
    f_unicore.write(message)
    f_unicore.close()

def dump_unicore_csv_file(qaas_reports_dir, file_name, table, best_only=False, best_options=None):
    '''Dump unicore runs to csv'''

    csv_unicore = open(os.path.join(qaas_reports_dir, file_name), "w", newline='\n')
    writer = csv.writer(csv_unicore)
    writer.writerow(['app_name', 'compiler', 'option #', 'flags', 'time(s)', 'Spd w.r.t orig', 'Spd w.r.t option 1'])
    
    # Write execution times to csv format
    for compiler in table:
        if not best_only:
            writer.writerows(table[compiler])
        else:
            writer.writerow(table[compiler][best_options[compiler]])
    csv_unicore.close()

def compute_unicore_speedups(t_unicore, orig_time, i_time):
    '''Compute Speedups w/r original and option 1 of compiler #1'''

    for compiler in t_unicore:
        for row  in t_unicore[compiler]:
            # Compare to user provided compiler and flags
            row.append(float(orig_time)/float(row[i_time]))
            # Compare to
            row.append(float(t_unicore[list(t_unicore.keys())[0]][0][i_time])/float(row[i_time]))

def measure_exec_times(app_name, base_run_dir, data_dir, run_cmd, compiled_options, maqao_dir):
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
            base_run_bin_dir = os.path.join(base_run_dir, 'unicore', f"{compiler}_{option}")
            basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', DEFAULT_REPETITIONS, "mpirun")
            tmp = [str(x) for x in basic_run.exec_times]
            # Check execution in defined range
            median_value = basic_run.compute_median_exec_time()
            run_log += f"[Compiler Options] (compiler={compiler},option={option}) Median on {DEFAULT_REPETITIONS} runs: {median_value}\n"
            time_values.append(median_value)
            t_compiler.append([app_name, compiler, option, flags, median_value])

            # Add extra OV runs: to be removed soon as not sustainable in production
            print("Run Extra OV")
            ov_run_dir_opt = os.path.join(ov_run_dir_root, f"{compiler}_{option}")
            oneview_runner.exec(app_env, binary_path, data_dir, ov_run_dir_opt, run_cmd, maqao_dir, None, 'both', level=1, mpi_run_command="mpirun", mpi_num_processes=1, ov_of="xlsx")

        # Add the local table to dict
        qaas_table[compiler] = t_compiler
        # Find best option for current compiler
        time_values = np.array(time_values)
        qaas_min_val = time_values.min()
        qaas_best_opt[compiler] = time_values.argmin()
        qaas_min_opt =  qaas_best_opt[compiler] + 1  # option indexing starts at 1.
        run_log += f"[Compiler Options] Fastest compilation {compiler} variant is {qaas_min_opt} with {qaas_min_val} seconds\n"


    return (qaas_table, qaas_best_opt, run_log)

def run_ov_on_best(ov_run_dir, ov_config, maqao_dir, data_dir, run_cmd, qaas_best_opt, compiled_options):
    '''Run and generate OneView reports on best options'''

    for compiler, best_opt in qaas_best_opt.items():
        # keep option directories consistent with build naming convention
        option = best_opt + 1
        # Setup experiment directory on oneview run directory
        ov_run_dir_opt = os.path.join(ov_run_dir, "unicore", f"{compiler}_{option}")
        # Extract the binary path of the best option
        binary_path = compiled_options[compiler][best_opt][0]
        # Retrieve the execution environment
        app_env = compiled_options[compiler][best_opt][1]
        # Make the oneview run
        oneview_runner.exec(app_env, binary_path, data_dir, ov_run_dir_opt, run_cmd, maqao_dir, ov_config, 'both', level=2, mpi_run_command="mpirun", mpi_num_processes=1)

def run_qaas_UP(app_name, src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                orig_user_CC, run_cmd, compiled_options, qaas_reports_dir, orig_time=1.0):
    '''Execute QAAS Running Logic: UNICORE PARAMETER EXPLORATION/TUNING'''

    # Init status
    rc=0
    # Compare options
    qaas_table, qaas_best_opt, log = measure_exec_times(app_name, base_run_dir, data_dir, run_cmd, compiled_options, maqao_dir)

    # Print log to file
    dump_unicore_log_file(qaas_reports_dir, 'qaas_unicore.log', log)
    #f_unicore.write(f"{str(qaas_best_opt)}\n")

    # Compute speedups
    index = 4 # index of the median execution time column
    compute_unicore_speedups(qaas_table, orig_time, index)

    # Dump csv table to file
    dump_unicore_csv_file(qaas_reports_dir, 'qaas_unicore.csv', qaas_table)
    # Dump best options csv file
    dump_unicore_csv_file(qaas_reports_dir, 'qaas_unicore_best.csv', qaas_table, True, qaas_best_opt)

    # Run oneview on best options
    run_ov_on_best(ov_run_dir, ov_config, maqao_dir, data_dir, run_cmd, qaas_best_opt, compiled_options)

    return rc,""
