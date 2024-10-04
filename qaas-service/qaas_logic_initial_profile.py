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

import app_builder
import app_runner
import lprof_runner
import oneview_runner
try:
   import app_mutator
except ImportError:
   pass
from logger import log, QaasComponents
from app_builder import build_argparser as app_builder_builder_argparser
from utils.util import parse_env_map
from utils import qaas_message as qm
from utils.comm import ServiceMessageSender
import utils.system as system
from utils.util import split_compiler_combo
from qaas_logic_compile import read_compiler_flags
from wrapper_runner import compiler_run
from qaas_logic_unicore import set_compilers_csv_header
from qaas_metadata import QAASMetaDATA

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))
LPROF_WALLTIME_LUA_FILE=os.path.join(script_dir, 'lua_scripts', 'lprof_walltime.lua')

DEFAULT_REPETITIONS = 11
MAX_ALLOWED_EXEC_TIME = 180

def compute_repetitions(stability):
    print(stability)
    if stability > 10:
        print("TODO UNSTABLE: aborting")
        return -1
    elif stability > 4:
        print("AVERAGE STABILITY: using 5 repetitions per run")
        return 5
    else:
        print("GOOD STABILITY: no repetitions")
        return 1

def dump_defaults_csv_file(qaas_reports_dir, file_name, table, timestamps, app_name, nb_mpi, nb_omp, flops, FOM):
    '''Dump compiler runs to csv'''

    csv_defaults = open(os.path.join(qaas_reports_dir, file_name), "w", newline='\n')
    writer = csv.writer(csv_defaults)
    writer.writerow(set_compilers_csv_header(table))

    # Write execution times to csv format
    for compiler in table:
        # Dump general information
        row = [timestamps[compiler], app_name, compiler, 0, 'default', nb_mpi, nb_omp]
        # Dump time and gflops
        if table[compiler] != None:
            row.extend([table[compiler], flops/float(table[compiler]), FOM[compiler]])
        else:
            row.extend([0.0, 0.0, 0.0])
        # Dump speedups
        for compiler_compare in table:
            if table[compiler] != None and table[compiler_compare] != None:
                row.append(float(table[compiler_compare])/float(table[compiler]))
            else:
                row.append(0.0)
        writer.writerow(row)
    csv_defaults.close()

def run_initial_profile(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location,
                     run_cmd, env_var_map, extra_cmake_flags, qaas_reports_dir,
                     disable_compiler_default, parallel_runs, multi_compilers_dirs):
    ''' Execute QAAS Running Logic: INITIAL PROFILING AND CLEANING'''

    # Parse original user CC
    mpi_wrapper, user_CC = split_compiler_combo(orig_user_CC)

    # Setup binary
    base_run_dir_orig = os.path.join(base_run_dir, 'defaults', 'orig')
    orig_binary = os.path.join(base_run_dir_orig, 'exec')

    # Build originl app using user-provided compilation options
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary,
                                   orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)
    # Add any user-provided environment variables
    app_builder_env.update(env_var_map)
    # Create sym links to orig build run folders
    subprocess.run([f"ln", "-s", "build", f"{user_CC}"], cwd=os.path.dirname(src_dir))
    subprocess.run([f"ln", "-s", "orig", f"{user_CC}"], cwd=os.path.dirname(base_run_dir_orig))

    # Setup run directory and launch initial run
    basic_run,nb_mpi,nb_omp = compiler_run(app_builder_env, orig_binary, data_dir, base_run_dir_orig, run_cmd,
                                           DEFAULT_REPETITIONS, "app", parallel_runs)
    print(basic_run.exec_times)
    tmp = [str(x) for x in basic_run.exec_times]

    # Check performance stability
    stability = basic_run.compute_stability_metric()
    new_repetitions = compute_repetitions(stability)
    if new_repetitions < 1:
        rc=-1
        error_msg='Stop profiling: execution times instable!'
        return rc,error_msg,0

    # Check execution in defined range
    median_value = basic_run.compute_median_exec_time()
    if median_value > MAX_ALLOWED_EXEC_TIME:
        rc=-1
        error_msg=f"ABORT: median execution time {median_value} greater than allowed {MAX_ALLOWED_EXEC_TIME}"
        return rc,error_msg,0
    # Dump median exec time to file
    with open(os.path.join(basic_run.run_dir, "initial_profile.csv"), "w") as csv_file:
        csv_file.write(f"base_median_time;{user_CC};" + str(median_value)+"\n")
    # Set dict of median values
    defaults = {}
    defaults['orig'] = median_value
    # Set dict of timestamps per compiler
    timestamps = {}
    timestamps['orig'] = basic_run.run_dir_timestamp
    # Set dict of per-compiler figure of merit
    figure_of_merit = {}
    if env_var_map.get("FOM_REGEX"):
        basic_run.match_figure_of_merit(env_var_map["FOM_REGEX"])
    figure_of_merit['orig'] = basic_run.compute_median_figure_of_merit()

    # Check LProf overhead
    lprof_run,_,_ = compiler_run(app_builder_env, orig_binary, data_dir, base_run_dir_orig, run_cmd,
                                 DEFAULT_REPETITIONS, "lprof", parallel_runs, maqao_dir)
    lprof_run.compute_lprof_time(LPROF_WALLTIME_LUA_FILE)
    new_lprof_conf = lprof_run.compute_lprof_overhead(median_value)
    print(new_lprof_conf)

    # Add debug compilation flags and rebuild app
    ov_run_dir_orig = os.path.join(ov_run_dir, 'defaults', 'orig')
    orig_binary = os.path.join(ov_run_dir_orig, 'exec')
    update_c_flags = f"{user_c_flags} -g -fno-omit-frame-pointer -fcf-protection=none -no-pie -grecord-gcc-switches"
    update_cxx_flags = f"{user_cxx_flags} -g -fno-omit-frame-pointer -fcf-protection=none -no-pie -grecord-gcc-switches"
    update_fc_flags = f"{user_fc_flags} -g -fno-omit-frame-pointer -fcf-protection=none -no-pie"
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary,
                                   orig_user_CC, target_CC, update_c_flags, update_cxx_flags, update_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)
    # Add any user-provided environment variables
    app_builder_env.update(env_var_map)
    # Create sym links to orig ov folder
    subprocess.run([f"ln", "-s", "orig", f"{user_CC}"], cwd=os.path.dirname(ov_run_dir_orig))
    #subprocess.run(f"ln -s orig {user_CC}", shell=True, cwd=os.path.dirname(ov_run_dir_orig))

    # Generate Level 2 oneview report on original app
    ov_run,_,_ = compiler_run(app_builder_env, orig_binary, data_dir, ov_run_dir_orig, run_cmd, DEFAULT_REPETITIONS, "oneview", parallel_runs, maqao_dir, ov_config)
    flops = 0 if ov_run == None else ov_run.extract_flops_count()

    # Run using other compilers with default flags
    if not disable_compiler_default:
        # Identify host machine vendor
        vendor = system.get_vendor_name()
        if vendor == 'unknown':
            print("Unknown / unsupported vendor")
            return None
        # Get the processor architecture
        processor = system.get_intel_processor_name(maqao_dir)

        # Get the list of flags for the CPU vendor (x86, ...) and processor.
        compiler_params = read_compiler_flags(vendor, processor)
        compilers_list = compiler_params['compilers']

        # Iterate on all compilers
        for compiler in compilers_list:
            # Nothing to do if user-specified compiler
            if compiler == user_CC:
                continue
            # Nothing to do if compiler if missing environment to load
            if not compiler in multi_compilers_dirs:
                print(f"Skip {compiler}. Missing compiler environment")
                continue

            # Set target compiler
            target_CC = f"{mpi_wrapper}-{compiler}" if mpi_wrapper else compiler
            # Setup binary
            base_run_bin_dir = os.path.join(base_run_dir, 'defaults', compiler)
            binary_path = os.path.join(base_run_bin_dir, 'exec')

            # Build originl app using user-provided compilation options
            app_builder_env = app_builder.exec(src_dir, multi_compilers_dirs[compiler], binary_path,
                                           orig_user_CC, target_CC, update_c_flags, update_cxx_flags, update_fc_flags,
                                           user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags, f"{compiler}")
            # Add any user-provided environment variables
            app_builder_env.update(env_var_map)

            # Setup run directory and launch initial run
            basic_run,_,_ = compiler_run(app_builder_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 3, "app", parallel_runs)
            defaults[compiler] = basic_run.compute_median_exec_time()
            timestamps[compiler] = basic_run.run_dir_timestamp
            # Extract Figure-of-Merit if any
            if env_var_map.get("FOM_REGEX"):
                basic_run.match_figure_of_merit(env_var_map["FOM_REGEX"])
            figure_of_merit[compiler] = basic_run.compute_median_figure_of_merit()

            # Dump median exec time to file
            with open(os.path.join(basic_run.run_dir, "initial_profile.csv"), "w") as csv_file:
                csv_file.write(f"base_median_time;{compiler};" + str(defaults[compiler])+"\n")

            # Make an OV run
            ov_run_bin_dir = os.path.join(ov_run_dir, 'defaults', compiler)
            compiler_run(app_builder_env, binary_path, data_dir, ov_run_bin_dir, run_cmd, DEFAULT_REPETITIONS, "oneview", parallel_runs, maqao_dir, ov_config)

    # Dump defaults values to csv
    dump_defaults_csv_file(qaas_reports_dir, 'qaas_compilers.csv', defaults, timestamps, user_target, nb_mpi,nb_omp, flops, figure_of_merit)

    # Dump meta data file (multi-compilers file and compiler drfault)
    qaas_meta = QAASMetaDATA(qaas_reports_dir)
    qaas_meta.add_prog_lang_metadata()
    qaas_meta.add_figure_of_merit_metadata("NA" if not env_var_map.get("FOM_REGEX") else env_var_map["FOM_TYPE"])
    qaas_meta.add_multicompiler_metadata(user_CC, 'qaas_compilers.csv')

    return 0,"",defaults,flops,nb_mpi,nb_omp
