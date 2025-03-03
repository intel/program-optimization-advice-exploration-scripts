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
import json
import pathlib

import app_builder
import app_runner
import lprof_runner
import oneview_runner
import utils.system as system
from logger import log, QaasComponents
from qaas_metadata import QAASMetaDATA

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))

DEFAULT_REPETITIONS = 1
CORES = [1, 2, 4, 8, 16, 32, 64, 128]
CORES_MIN_THRESHOLD = 30.0
SMALL_SYSTEM_CORES  = 128

def dump_multicore_log_file(qaas_reports_dir, file_name, message):
    '''Dump multicore runs log'''

    f_unicore = open(os.path.join(qaas_reports_dir, file_name), "w")
    f_unicore.write(message)
    f_unicore.close()

def dump_multicore_csv_file(qaas_reports_dir, file_name, table, best_only=False, best_options=None):
    '''Dump unicore runs to csv'''

    # Open multicore runs CSV file
    csv_unicore = open(os.path.join(qaas_reports_dir, file_name), "w", newline='\n')
    writer = csv.writer(csv_unicore)
    # Setup header
    csv_header= ['timestamp', 'app_name', 'compiler', 'option #', '#MPI', '#OMP', 'affinity', 'time(s)', 'GFlops/s', 'FOM']
    for compiler in table:
        csv_header.append(f"Spd w.r.t {compiler}")
    writer.writerow(csv_header)

    # Write execution times to csv format
    for compiler in table:
        if not best_only:
            writer.writerows(table[compiler])
        else:
            writer.writerow(table[compiler][best_options[compiler]])
    csv_unicore.close()

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
    # Get maximum number of physical cores available in the system
    max_nodes = system.get_number_of_nodes()
    # Compute the logarithl base 2 of the maximum number of cores (get power of 2 index)
    max_power_of_2 = int(math.log2(max_cores))
    # build the array of the number of cores to scale
    SF = max_nodes*4 if max_nodes > 4 else max_nodes*8
    half_cores = int(int(max_cores/max_nodes)*max_nodes/2)
    cores = [max_nodes*2**c for c in range(0,max_power_of_2+1)] + [half_cores, 2**max_power_of_2, max_cores] + [c for c in range(SF,max_cores,SF)]
    # Get rid from duplicates, remove any number greater than max_cores and sort new list
    cores = [core for core in sorted(list(set(cores))) if core <= max_cores]

    return cores

def update_runs_table(fixed_run_params, parallel_run_params):
    '''Add meta information (fixed run params) to parallel runs configurations'''

    return [ [item[0]] + fixed_run_params + item[1:] for item in parallel_run_params ]

def run_scalability_mpi(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions=1, affinity="scatter"):
    '''Perform a scalability analysis using only MPI'''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    nb_nodes = system.get_number_of_nodes()
    # Set compact range limits
    min_limit = 0
    max_limit = nb_cores-1
    # Set process affinity policy environment variables
    mpi_provider = app_env['MPI_PROVIDER']
    mpi_env_affinity = {"I_MPI_PIN_DOMAIN":"auto", "I_MPI_PIN_ORDER":"spread", "I_MPI_DEBUG":"4"} if affinity == "scatter" else {"I_MPI_PIN_PROCESSOR_LIST":f"{min_limit}-{max_limit}", "I_MPI_DEBUG":"4"}

    omp_env_affinity = {"OMP_PLACES":"threads","OMP_PROC_BIND":"spread"}
    omp_env_affinity.update({"OMP_DISPLAY_ENV":"TRUE","OMP_DISPLAY_AFFINITY":"TRUE","OMP_AFFINITY_FORMAT":"OMP: pid %P tid %i thread %n bound to OS proc set {%A}"})
    # Compute array of possible scaling configurations
    scale_cores = compute_scaling_cores()

    p_runs = []
    # Sweep through all core configurations
    for cores in scale_cores:
        # Skip low core count runs on large systems
        if nb_cores >= SMALL_SYSTEM_CORES  and cores != nb_nodes and cores/nb_cores*100 < CORES_MIN_THRESHOLD:
            continue
        # Skip compact affinity runs when #cores is more than the size of a socket
        if affinity == "compact" and cores > nb_cores/2:
            continue
        if mpi_provider == "OpenMPI":
            mpi_env_affinity = {'QAAS_OPENMPI_BIND_CMD':f'--bind-to core --map-by package:PE={int(nb_cores/cores)} --rank-by fill --report-bindings'} if affinity == "scatter" else {'QAAS_OPENMPI_BIND_CMD':f'--bind-to core --map-by pe-list={",".join([str(i) for i in range(0,max_limit+1,1)])}:ordered  --report-bindings'}
        # Make the runs
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', repetitions, "mpirun",
                                mpi_num_processes=cores, omp_num_threads=1, mpi_envs=mpi_env_affinity, omp_envs=omp_env_affinity)
        # Extract Figure-of-Merit if any
        if app_env.get("FOM_REGEX"):
            basic_run.match_figure_of_merit(app_env["FOM_REGEX"])
        FOM = basic_run.compute_median_figure_of_merit()
        # Get the median execution time
        p_runs.append([basic_run.run_dir_timestamp, cores, 1, affinity, basic_run.compute_median_exec_time(), FOM])

    return p_runs

def run_scalability_omp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions=1, affinity="scatter"):
    '''Perform a scalability analysis for OMP apps. '''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    nb_nodes = system.get_number_of_nodes()
    # Set compact range limits
    min_limit = 0
    max_limit = nb_cores-1
    # Set process affinity policy environment variables
    mpi_provider = app_env['MPI_PROVIDER']
    mpi_env_affinity = {'QAAS_OPENMPI_BIND_CMD':'--bind-to none --report-bindings'} if mpi_provider == "OpenMPI" else {"I_MPI_PIN_DOMAIN":"auto","I_MPI_PIN_ORDER":"spread", "I_MPI_DEBUG":"4"}
    omp_env_affinity = {"OMP_PLACES":"threads","OMP_PROC_BIND":"spread"} if affinity == "scatter" else {"OMP_PLACES":','.join(['{'+str(i)+'}' for i in range(min_limit,max_limit+1,1)]),"OMP_PROC_BIND":"close"}
    omp_env_affinity.update({"OMP_DISPLAY_ENV":"TRUE","OMP_DISPLAY_AFFINITY":"TRUE","OMP_AFFINITY_FORMAT":"OMP: pid %P tid %i thread %n bound to OS proc set {%A}"})
    # Compute array of possible scaling configurations
    scale_cores = compute_scaling_cores()
    # Check any pattern to extract for FOM
    pattern = app_env["FOM_REGEX"] if app_env.get("FOM_REGEX") else ""

    p_runs = []
    # Sweep through all core configurations
    for cores in scale_cores:
        # Skip low core count runs on large systems
        if nb_cores >= SMALL_SYSTEM_CORES and cores != nb_nodes and cores/nb_cores*100 < CORES_MIN_THRESHOLD:
            continue
        # Skip compact affinity runs when #cores is more than the size of a socket
        if affinity == "compact" and cores > nb_cores/2:
            continue
        # Make the runs
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', repetitions, "mpirun",
                                mpi_num_processes=1, omp_num_threads=cores, mpi_envs=mpi_env_affinity, omp_envs=omp_env_affinity)
        # Extract Figure-of-Merit if any
        if app_env.get("FOM_REGEX"):
            basic_run.match_figure_of_merit(app_env["FOM_REGEX"])
        FOM = basic_run.compute_median_figure_of_merit()
        # Get the median execution time
        p_runs.append([basic_run.run_dir_timestamp, 1, cores, affinity, basic_run.compute_median_exec_time(), FOM])

    return p_runs

def run_scalability_mpixomp(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, repetitions=1):
    '''Perform a scalability analysis for OMP apps. '''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    nb_nodes = system.get_number_of_nodes()
    # Set process affinity policy environment variables
    mpi_provider = app_env['MPI_PROVIDER']
    mpi_env_affinity = {"I_MPI_PIN_DOMAIN":"auto","I_MPI_PIN_ORDER":"spread", "I_MPI_DEBUG":"4"}
    omp_env_affinity = {"OMP_PLACES":"threads","OMP_PROC_BIND":"spread"}
    omp_env_affinity.update({"OMP_DISPLAY_ENV":"TRUE","OMP_DISPLAY_AFFINITY":"TRUE","OMP_AFFINITY_FORMAT":"OMP: pid %P tid %i thread %n bound to OS proc set {%A}"})
    # Compute array of possible scaling configurations
    scale_cores = compute_scaling_cores()

    p_runs = []
    # Sweep through all core configurations
    for mpi_ranks in sorted(list(set(scale_cores+[int(c/2) for c in scale_cores][1:]))):
        if mpi_ranks % nb_nodes != 0:
            continue
        if mpi_provider == "OpenMPI":
            mpi_env_affinity = {'QAAS_OPENMPI_BIND_CMD':f'--bind-to core --map-by package:PE={int(nb_cores/mpi_ranks)} --rank-by fill --report-bindings'} 
        # Cut in half the number of omp threads available as the number of MPI ranks increases
        nb_threads_list = sorted(list(set([int(th/(mpi_ranks)) for th in scale_cores])))
        for omp_threads in nb_threads_list:
            # Continue of the computed number of threads is less or equal to 1
            if omp_threads <= 1:
                continue
            # Skip low core count runs on large systems
            if nb_cores >= SMALL_SYSTEM_CORES and (mpi_ranks*omp_threads)/nb_cores*100 < CORES_MIN_THRESHOLD:
                continue
            # Make the runs
            basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', repetitions, "mpirun",
                                mpi_num_processes=mpi_ranks, omp_num_threads=omp_threads, mpi_envs=mpi_env_affinity, omp_envs=omp_env_affinity)
            # Extract Figure-of-Merit if any
            if app_env.get("FOM_REGEX"):
                basic_run.match_figure_of_merit(app_env["FOM_REGEX"])
            FOM = basic_run.compute_median_figure_of_merit()
            # Get the median execution time
            p_runs.append([basic_run.run_dir_timestamp, mpi_ranks, omp_threads, "scatter", basic_run.compute_median_exec_time(), FOM])

    return p_runs

def eval_parallel_scale(app_name, base_run_dir, data_dir, run_cmd, qaas_best_opt, compiled_options, has_mpi, has_omp, mpi_weak, omp_weak, flops_per_app, bestcomp=None):
    '''Measure Application-wide execution times'''

    # Compare options
    run_log=""
    mp_best_opt = dict()
    qaas_table = dict()
    for compiler, best_opt in qaas_best_opt.items():
        # Nothing to do if bestcomp != from compiler
        if bestcomp != None and bestcomp != compiler:
            continue
        # Ignore #MPI and #OMP keys in per-compiler bestopt
        if compiler == 'MPI' or compiler == 'OMP':
            continue
        # keep option directories consistent with build naming convention
        option = best_opt['index'] + 1
        # Setup experiment directory on base run directory
        base_run_bin_dir = os.path.join(base_run_dir, 'multicore', best_opt['build'])
        # Setup run parameters for a specific compiler
        binary_path, app_env, flags = set_run_params(best_opt['index'], compiled_options[compiler])

        # Init arrays
        t_compiler = []
        # Setup number of iterations 
        repetitions = DEFAULT_REPETITIONS

        # Make a single core run for reference in scalability analysis
        if system.get_number_of_cores() < SMALL_SYSTEM_CORES or mpi_weak:
            basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_bin_dir, run_cmd, 'both', 1, "mpirun", mpi_num_processes=1)
            # Extract Figure-of-Merit if any
            if app_env.get("FOM_REGEX"):
                basic_run.match_figure_of_merit(app_env["FOM_REGEX"])
            FOM = basic_run.compute_median_figure_of_merit()
            t_compiler.append([basic_run.run_dir_timestamp, app_name, compiler, option, 1, 1, "ref.", basic_run.compute_median_exec_time(), FOM])

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

def generate_ov_config_multiruns(ov_run_dir, nb_mpi, nb_omp, has_mpi, has_omp, affinity):
    '''Create multi-runs OV configuration'''

    # Find OV config.json of bestcomp
    bestcomp = os.path.relpath(ov_run_dir, os.path.join(ov_run_dir, '..', '..')).split('/')[1]
    mc_base = 'compilers' if len(bestcomp.split('_')) == 2 else 'defaults'
    bestcomp_path = os.path.join(os.path.abspath(os.path.join(ov_run_dir, "..", "..")), mc_base, bestcomp)
    config_file = list(pathlib.Path(bestcomp_path).glob('oneview_run_*/config.json'))[0]
    # Init JSON config from bestcomp run
    config = {}
    with open(config_file, "r") as read_file:
        config = json.load(read_file)

    # Update number of processes and openmp threads
    config["config"]["number_processes"]  = nb_mpi if (has_mpi and nb_mpi < system.get_number_of_cores()) or nb_mpi == 1 else system.get_number_of_nodes()
    config["config"]["envv_OMP_NUM_THREADS"] = 1 if has_mpi else system.get_number_of_nodes()
    # Add a comment section to specify compiler
    config["config"]["comments"] = f"OV scalability run using {bestcomp}"
    # Update base_run_name
    config["config"]["base_run_name"] = f'{config["config"]["number_processes"]}x{config["config"]["envv_OMP_NUM_THREADS"]}'
    # Update run_dir
    config["config"]["run_directory"] = ""
    # Print multi runs params
    mpconf = []
    nb_cores = system.get_number_of_cores()
    scale_cores = compute_scaling_cores()
    for cores in scale_cores:
        mpi = 1
        omp = 1
        if nb_mpi == nb_cores:
            # scale MPI only
            mpi = cores
        elif nb_mpi != 1:
            # scale omp in hybrid mode
            mpi = config["config"]["number_processes"]
            omp = int(cores / config["config"]["number_processes"])
        else:
            # scale OpenMP only (no MPI)
            omp = cores
        if (mpi == 0 or omp == 0) or (config["config"]["number_processes"] * config["config"]["envv_OMP_NUM_THREADS"] >= mpi * omp):
            continue
        # Skip low core count runs on large systems
        if nb_cores >= SMALL_SYSTEM_CORES and mpi*omp/nb_cores*100 < CORES_MIN_THRESHOLD:
            continue
        mpconf.append({"name":f'{mpi}x{omp}', "number_processes":mpi, "envv_OMP_NUM_THREADS":omp})
    config["config"]["multiruns_params"] = mpconf
    # Setup environment variables to control affinity
    for var,value in affinity.items():
        config["config"][f"envv_{var}"] = value

    # Write configuration to file
    os.makedirs(ov_run_dir)
    ov_config = os.path.join(ov_run_dir, f"config.json")
    with open(ov_config, "w") as write_file:
        json.dump(config, write_file, indent=4)
    return ov_config

def run_ov_on_best(ov_run_dir, maqao_dir, data_dir, run_cmd,
                   qaas_best_opt, bestcomp, compiled_options,
                   has_mpi, has_omp, weak_scale, qaas_reports_dir):
    '''Run and generate OneView reports on best options'''

    best_opt = qaas_best_opt[bestcomp]
    # keep option directories consistent with build naming convention
    option = best_opt['index'] + 1
    # Setup experiment directory on oneview run directory
    ov_run_dir_opt = os.path.join(ov_run_dir, "multicore", best_opt['build'])
    # Extract the binary path of the best option
    binary_path = compiled_options[bestcomp][best_opt['index']][0]
    # Retrieve the execution environment
    app_env = compiled_options[bestcomp][best_opt['index']][1]
    mpi_provider = app_env['MPI_PROVIDER']
    # Setup MPI and OpenMP affinity env vars
    affinity = {"OMP_PLACES":"threads", "OMP_PROC_BIND":"spread"}
    affinity.update({"OMP_DISPLAY_ENV":"TRUE","OMP_DISPLAY_AFFINITY":"TRUE","OMP_AFFINITY_FORMAT":"'OMP: pid %P tid %i thread %n bound to OS proc set {%A}'"})
    if mpi_provider == "IntelMPI":
        affinity.update({"I_MPI_PIN_DOMAIN":"auto","I_MPI_PIN_ORDER":"bunch", "I_MPI_DEBUG":"4"})
    # Create a multi-runs OV configuration
    ov_config = generate_ov_config_multiruns(ov_run_dir_opt, qaas_best_opt["MPI"], qaas_best_opt["OMP"], has_mpi, has_omp, affinity)
    # Specify what OV scaling mode to enforce
    app_env["OV_SCALE"] = "-WS" if not weak_scale else "-WS=weak"
    # Make the oneview run
    ov_run = oneview_runner.exec(app_env, binary_path, data_dir, ov_run_dir_opt, run_cmd, maqao_dir, ov_config, 'both', level=1, mpi_run_command=None,
                        mpi_num_processes=1, omp_num_threads=1, mpi_envs={}, omp_envs={})
    if ov_run != None:
        ov_run.move_multicore_html_report(qaas_reports_dir)


def compute_gflops(flops_per_app, time, nmpi, nomp, has_mpi, has_omp, mpi_weak, omp_weak):
    '''Compute GFlops/s depending on MPI and/or OpenMP scaling modes'''
    if mpi_weak and omp_weak:
        gflops = flops_per_app * nmpi * nomp / time
    elif mpi_weak and (not has_omp or not omp_weak):
        gflops = flops_per_app * nmpi / time
    elif omp_weak and (not has_mpi or not mpi_weak):
        gflops = flops_per_app * nomp / time
    else:
        gflops = flops_per_app / time
    return gflops

def add_gflops_to_runs(p_runs, flops_per_app, i_time, i_mpi, i_omp, has_mpi, has_omp, mpi_weak, omp_weak):
    '''Add GFlops/s to all parallel runs'''

    for compiler in p_runs:
        for run in p_runs[compiler]:
            if run[i_time] != None:
                #run.append(compute_gflops(flops_per_app, run[i_time], run[i_mpi], run[i_omp], has_mpi, has_omp, mpi_weak, omp_weak))
                run.insert(i_time + 1, compute_gflops(flops_per_app, run[i_time], run[i_mpi], run[i_omp], has_mpi, has_omp, mpi_weak, omp_weak))
            else:
                #run.append(0.0)
                run.insert(i_time + 1, 0.0)

def add_speedups_to_runs(p_runs, i_time, i_mpi, i_omp, has_mpi, has_omp, mpi_weak, omp_weak):
    '''Compute Speedups w/r to smallest cores count per compiler'''

    # Search reference runs
    mp_ref_runs = {}
    ref_lines = {}
    offset = 0 # Fix: SPD found offset uninitialized
    for c in range(0, len(p_runs)):
        compiler = list(p_runs.keys())[c]
        index = 1 # start at 1 because of CSV header
        for run in p_runs[compiler]:
            index = index + 1 # line numbering start from 1 not 0
            # Find per-compiler baseline: #MPIx1 if MPI or hybrid or First OpenMP configuration
            if run[i_time] != None and (run[i_omp] == 1 or (not has_mpi and run[i_omp] >= 1)):
                # find the first valid run (!= None)
                mp_ref_runs[compiler] = [run[i_time], run[i_mpi], run[i_omp]]
                break
        if not compiler in mp_ref_runs:
            # all runs for this compiler have failed
            mp_ref_runs[compiler] = [0.0, 0, 0]
            index = 0
        offset = offset + len(p_runs[list(p_runs.keys())[c-1]]) if c > 0 else 0
        ref_lines[compiler] = index + offset if index > 0 else 0

    # Compute speedups
    for compiler in p_runs:
        for run  in p_runs[compiler]:
            for item in mp_ref_runs:
                if run[i_time] != None:
                    # Compute replication factor
                    if mpi_weak and omp_weak:
                        replication = run[i_mpi] * run[i_omp]
                    elif mpi_weak:
                        replication = run[i_mpi]
                    elif omp_weak:
                        replication = run[i_omp]
                    else:
                        replication = 1 * mp_ref_runs[item][1] *  mp_ref_runs[item][2]
                    # Compare to user provided compiler and flags
                    run.append(mp_ref_runs[item][0] * replication / float(run[i_time]))
                else:
                    # Compare to
                    run.append(0.0)
    return ",".join([item+':'+str(ref_lines[item]) for item in ref_lines])

def run_qaas_MP(app_name, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                orig_user_CC, run_cmd, compiled_options, qaas_best_opt, qaas_best_comp, qaas_reports_dir,
                has_mpi=True, has_omp=True, mpi_weak=False, omp_weak=False, flops_per_app=0.0, scale_best_comp=False):
    '''Execute QAAS Running Logic: MULTICORE PARAMETER EXPLORATION/TUNING'''

    # Init status
    rc=0
    # Check if no parallelism through MPI and/or OMP
    if not has_mpi and not has_omp:
        return rc,None,""

    # Compare options
    bestcomp_only = qaas_best_comp if scale_best_comp else None
    qaas_table, mp_best_opt, log = eval_parallel_scale(app_name, base_run_dir, data_dir, run_cmd, qaas_best_opt, compiled_options,
                                                       has_mpi, has_omp, mpi_weak, omp_weak, flops_per_app, bestcomp_only)

    # Set index of the median execution time column
    i_time = 7
    # Set indexs of the number of MPI processes and OpenMP thraeds
    i_mpi = 4
    i_omp = 5
    # Update run tables with GFlops/s
    add_gflops_to_runs(qaas_table, flops_per_app, i_time, i_mpi, i_omp, has_mpi, has_omp, mpi_weak, omp_weak)
    # Update run tables with Speedups/s
    ref_lines = add_speedups_to_runs(qaas_table, i_time, i_mpi, i_omp, has_mpi, has_omp, mpi_weak, omp_weak)

    # Print log to file
    dump_multicore_log_file(qaas_reports_dir, 'qaas_multicore.log', log)

    # Dump csv table to file
    dump_multicore_csv_file(qaas_reports_dir, 'qaas_multicore.csv', qaas_table)

    # Run a oneview scalability run on best compiler/option
    run_ov_on_best(ov_run_dir, maqao_dir, data_dir, run_cmd, qaas_best_opt, qaas_best_comp, compiled_options, has_mpi, has_omp, mpi_weak | omp_weak, qaas_reports_dir)

    # Dump meta data file
    qaas_meta = QAASMetaDATA(qaas_reports_dir)
    qaas_meta.add_scalability_metadata("", "", 'qaas_multicore.csv', ref_lines)

    return rc,mp_best_opt,""
