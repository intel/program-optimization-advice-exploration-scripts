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
# Created June 2023
# Contributors: Hafid/David

from argparse import ArgumentParser
import subprocess
import os
import sys
import csv
import math
import numpy as np

import app_builder
import app_runner
import lprof_runner
import oneview_runner
import utils.system as system
from logger import log, QaasComponents

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))

DEFAULT_REPETITIONS = 3
CORES = [1, 2, 4, 8, 16, 32, 64, 128]

def dump_multicore_log_file(qaas_reports_dir, file_name, message):
    '''Dump multicore runs log'''

    f_unicore = open(os.path.join(qaas_reports_dir, file_name), "w")
    f_unicore.write(message)
    f_unicore.close()

def dump_multicore_csv_file(qaas_reports_dir, file_name, table, best_only=False, best_options=None):
    '''Dump unicore runs to csv'''

    csv_unicore = open(os.path.join(qaas_reports_dir, file_name), "w", newline='\n')
    writer = csv.writer(csv_unicore)
    writer.writerow(['app_name', 'compiler', 'option #', '#MPI', '#OMP', 'affinity', 'time(s)'])
    
    # Write execution times to csv format
    for compiler in table:
        if not best_only:
            writer.writerows(table[compiler])
        else:
            writer.writerow(table[compiler][best_options[compiler]])
    csv_unicore.close()

#def compute_unicore_speedups(t_unicore, orig_time, i_time):
#    '''Compute Speedups w/r original and option 1 of compiler #1'''
#
#    for compiler in t_unicore:
#        for row  in t_unicore[compiler]:
#            # Compare to user provided compiler and flags
#            row.append(float(orig_time)/float(row[i_time]))
#            # Compare to
#            row.append(float(t_unicore[list(t_unicore.keys())[0]][0][i_time])/float(row[i_time]))

def eval_parallel_stability(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, has_mpi, has_omp):
    '''Evaluate Multicore runs stability for apps that use MPI, OpenMP (OMP) or hybrid MPIxOMP'''
   
    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    nb_sockets = system.get_number_of_sockets()

    # run a stability analysis depending on parallel runtime characteristics
    if has_mpi and has_omp:
        # Stability for hybrid MPIxOMP mode
        mpi_ranks = nb_sockets 
        omp_threads = int(nb_cores / nb_sockets)
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', 11, "mpirun", 
                                    mpi_num_processes=mpi_ranks, omp_num_threads=omp_threads,
                                    mpi_envs={"I_MPI_PIN_DOMAIN":"auto:scatter"},
                                    omp_envs={"OMP_PLACES":"threads", "OMP_PROC_BIND":"spread"})
    elif has_mpi:
        # Stability for pure MPI mode
        mpi_ranks = nb_cores
        omp_threads = 1 
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', 11, "mpirun", 
                                    mpi_num_processes=mpi_ranks, omp_num_threads=omp_threads,
                                    mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=scatter"})
    elif has_omp:
        # Stability for pure OMP mode
        mpi_ranks = 1 
        omp_threads = nb_cores
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', 11, "mpirun",
                                    mpi_num_processes=mpi_ranks, omp_num_threads=omp_threads,
                                    mpi_envs={"I_MPI_PIN_DOMAIN":"auto:scatter"},
                                    omp_envs={"OMP_PLACES":"threads", "OMP_PROC_BIND":"spread"})

    # Compute median execution time and check stability
    median_time = basic_run.compute_median_exec_time()
    stability = basic_run.compute_stability_metric()
    # Compute stability
    if stability > 10:
        status = (-1, 0, None, None)
    elif stability > 3:
        status = (3, median_time, mpi_ranks, omp_threads)
    else:
        status = (1, median_time, mpi_ranks, omp_threads)

    return status

def set_run_params(best_opt_index, compiled_options):
    '''Find and set run parameters for best compiler/options configuration.'''

    # Extract the binary path of the best option
    binary_path = compiled_options[best_opt_index][0]
    # Retrieve the execution environment
    app_env = compiled_options[best_opt_index][1]
    # Retrieve the flags 
    flags = compiled_options[best_opt_index][2]

    return binary_path,app_env,flags

def compute_scaling_cores():
    '''Compute array of cores configurations for parallel scaling'''

    # Get maximum number of physical cores available in the system
    max_cores = system.get_number_of_cores()
    # Compute the logarithl base 2 of the maximum number of cores (get power of 2 index) 
    max_power_of_2 = int(math.log2(max_cores))
    # build the array of the number of cores to scale
    cores = [2**c for c in range(1,max_power_of_2+1)]
    # Append max physical cores to array if missing
    if max_cores >= 2**max_power_of_2:
        cores.append(max_cores)

    return cores

def update_runs_table(fixed_run_params, parallel_run_params):
    '''Add meta information (fixed run params) to parallel runs configurations'''

    return [ fixed_run_params + item for item in parallel_run_params ]

def run_scalability_mpi(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions=1, affinity="scatter"):
    '''Perform a scalability analysis using only MPI'''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    # Set compact range limits
    min_limit = 0
    max_limit = nb_cores-1
    # Set process affinity policy environment variables
    mpi_env_affinity = {"I_MPI_PIN_PROCESSOR_LIST":"all:map=scatter"} if affinity == "scatter" else {"I_MPI_PIN_PROCESSOR_LIST":f"{min_limit}-{max_limit}"}
    # Compute array of possible scaling configurations
    scale_cores = compute_scaling_cores()

    p_runs = []
    # Sweep through all core configurations
    for cores in scale_cores:
        # Make the runs
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', repetitions, "mpirun", 
                                mpi_num_processes=cores, omp_num_threads=1, mpi_envs=mpi_env_affinity)
        # Get the median execution time
        p_runs.append([cores, 1, affinity, basic_run.compute_median_exec_time()])

    return p_runs

def run_scalability_omp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions=1, affinity="scatter"):
    '''Perform a scalability analysis for OMP apps. '''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    # Set compact range limits
    min_limit = 0
    max_limit = nb_cores-1
    # Set process affinity policy environment variables
    mpi_env_affinity = {"I_MPI_PIN_DOMAIN":"auto:scatter"} 
    omp_env_affinity = {"OMP_PLACES":"threads","OMP_PROC_BIND":"spread"} if affinity == "scatter" else {"GOMP_CPU_AFFINITY":f"{min_limit}-{max_limit}"}
    # Compute array of possible scaling configurations
    scale_cores = compute_scaling_cores()

    p_runs = []
    # Sweep through all core configurations
    for cores in scale_cores:
        # Make the runs
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', repetitions, "mpirun", 
                                mpi_num_processes=1, omp_num_threads=cores, mpi_envs=mpi_env_affinity, omp_envs=omp_env_affinity)
        # Get the median execution time
        p_runs.append([1, cores, affinity, basic_run.compute_median_exec_time()])

    return p_runs

def run_scalability_mpixomp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions=1):
    '''Perform a scalability analysis for OMP apps. '''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    # Set process affinity policy environment variables
    mpi_env_affinity = {"I_MPI_PIN_DOMAIN":"auto:scatter"} 
    omp_env_affinity = {"OMP_PLACES":"threads","OMP_PROC_BIND":"spread"}
    # Compute array of possible scaling configurations
    scale_cores = [int(c/2) for c in compute_scaling_cores()]
    del scale_cores[0]

    p_runs = []
    # Sweep through all core configurations
    for mpi_ranks in scale_cores:
        # Cut in half the number of omp threads available as the number of MPI ranks increases
        nb_threads_list = [int(th/(mpi_ranks/2)) for th in scale_cores]
        for omp_threads in nb_threads_list:
            # Continue of the computed number of threads is less or equal to 1
            if omp_threads <= 1:
                continue
            # Make the runs
            basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', repetitions, "mpirun", 
                                mpi_num_processes=mpi_ranks, omp_num_threads=omp_threads, mpi_envs=mpi_env_affinity, omp_envs=omp_env_affinity)
            # Get the median execution time
            p_runs.append([mpi_ranks, omp_threads, "scatter", basic_run.compute_median_exec_time()])

    return p_runs


def eval_parallel_scale(app_name, base_run_dir, data_dir, run_cmd, qaas_best_opt, compiled_options, has_mpi, has_omp, mpi_weak, omp_weak):
    '''Measure Application-wide execution times'''

    # Compare options
    run_log=""
    mp_best_opt = dict()
    qaas_table = dict()
    for compiler, best_opt in qaas_best_opt.items():
        # keep option directories consistent with build naming convention
        option = best_opt + 1
        # Setup experiment directory on base run directory
        base_run_bin_dir = os.path.join(base_run_dir, 'multicore', f"{compiler}_{option}")
        # Setup run parameters for a specific compiler
        binary_path, app_env, flags = set_run_params(best_opt, compiled_options[compiler])

        # Init arrays
        t_compiler = []

        # First stability run
        repetitions, median_time, nmpi, nomp = eval_parallel_stability(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, has_mpi, has_omp)
        if repetitions == -1:
            print(f"Stop parallel runs for compiler {compiler}: too unstable!")
            continue
        t_compiler.append([app_name, compiler, option, nmpi, nomp, "scatter", median_time])

        # Make a single core run for reference in scalability analysis
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', 1, "mpirun", mpi_num_processes=1)
        t_compiler.append([app_name, compiler, option, 1, 1, "ref.", basic_run.compute_median_exec_time()])

        # Perform a scalability analysis using a pure MPI mode and varying process affinity policy
        if has_mpi:
            # MPI runs using the Scatter policy
            p_runs = run_scalability_mpi(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions, "scatter")
            t_compiler += update_runs_table([app_name, compiler, option], p_runs)
            # MPI runs using the Compact policy
            p_runs = run_scalability_mpi(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions, "compact")
            t_compiler += update_runs_table([app_name, compiler, option], p_runs)

        # Perform a scalability analysis using a pure MPI mode and varying process affinity policy
        if has_omp:
            # OMP runs using the Scatter policy
            p_runs = run_scalability_omp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions, "scatter")
            t_compiler += update_runs_table([app_name, compiler, option], p_runs)
            # OMP runs using the Compact policy
            p_runs = run_scalability_omp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions, "compact")
            t_compiler += update_runs_table([app_name, compiler, option], p_runs)

        # Perform a scalability analysis using a pure MPI mode and varying process affinity policy
        if has_mpi and has_omp:
            # Hybrid MPI x OMP runs
            p_runs = run_scalability_mpixomp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions)
            t_compiler += update_runs_table([app_name, compiler, option], p_runs)
       
        # Add the local table to dict
        qaas_table[compiler] = t_compiler

    return (qaas_table, mp_best_opt, run_log)

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

def run_qaas_MP(app_name, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                orig_user_CC, run_cmd, compiled_options, qaas_best_opt, qaas_reports_dir,
                has_mpi=True, has_omp=True, mpi_weak=False, omp_weak=False):
    '''Execute QAAS Running Logic: UNICORE PARAMETER EXPLORATION/TUNING'''

    # Init status
    rc=0

    # Check if no parallelism through MPI and/or OMP
    if not has_mpi and not has_omp:
        return rc,None,""

    # Compare options
    qaas_table, mp_best_opt, log = eval_parallel_scale(app_name, base_run_dir, data_dir, run_cmd, qaas_best_opt, compiled_options,
                                                       has_mpi, has_omp, mpi_weak, omp_weak)

    # Print log to file
    dump_multicore_log_file(qaas_reports_dir, 'qaas_multicore.log', log)

    # Compute speedups
    #index = 6 # index of the median execution time column

    # Dump csv table to file
    dump_multicore_csv_file(qaas_reports_dir, 'qaas_multicore.csv', qaas_table)
    # Dump best options csv file

    # Run oneview on best options

    return rc,mp_best_opt,""
