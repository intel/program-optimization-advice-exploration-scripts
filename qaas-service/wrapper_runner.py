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
# Created September 2023
# Contributors: Hafid/David

import app_runner
import lprof_runner
import oneview_runner
import utils.system as system

def run_app(app_env, binary, data_dir, run_dir, run_cmd, repetitions, runtype,
            nb_ranks, nb_threads, mpi_affinity, omp_affinity,
            maqao_dir=None, ov_config=None):
    '''Wrapper runner for unicore and multicore runs'''

    if runtype == "app":
        # Invoque base runner
        new_run = app_runner.exec(app_env, binary, data_dir, run_dir, run_cmd,
                                  'both', repetitions, "mpirun",
                                  mpi_num_processes=nb_ranks, omp_num_threads=nb_threads,
                                  mpi_envs=mpi_affinity, omp_envs=omp_affinity)
    elif runtype == "lprof":
        # Invoque lprof runner
        new_run = lprof_runner.exec(app_env, binary, maqao_dir, run_dir, data_dir, run_cmd,
                                    'both', "mpirun",
                                    mpi_num_processes=nb_ranks, omp_num_threads=nb_threads,
                                    mpi_envs=mpi_affinity, omp_envs=omp_affinity)
    elif runtype == "oneview":
        # Invoque oneview runner
        new_run = oneview_runner.exec(app_env, binary, data_dir, run_dir, run_cmd, maqao_dir, ov_config,
                                      mode='both', level=1, mpi_run_command="mpirun",
                                      mpi_num_processes=nb_ranks, omp_num_threads=nb_threads,
                                      mpi_envs=mpi_affinity, omp_envs=omp_affinity)

    return new_run

def compiler_run(app_env, binary, data_dir, run_dir, run_cmd, repetitions, runtype, parallel_runs, maqao_dir=None, ov_config=None):
    '''Wrapper runner to set running parameters for QaaS compiler search runs'''

    # Get system/topology information
    nb_cores = system.get_number_of_cores()
    nb_nodes = system.get_number_of_nodes()
    nb_cores_per_node = int(nb_cores / nb_nodes)
    max_limit = nb_cores-1

    if parallel_runs == 'mpi':
        # Multicore MPI runs
        nb_ranks = nb_cores
        nb_threads = 1
        mpi_affinity = {"I_MPI_PIN_PROCESSOR_LIST":f"0-{max_limit}"}
        omp_affinity = {}
    elif parallel_runs == 'openmp':
        # Multicore OpenMP runs
        nb_ranks = 1
        nb_threads = nb_cores
        mpi_affinity = {"I_MPI_PIN_DOMAIN":"auto:scatter"}
        omp_affinity = {"GOMP_CPU_AFFINITY":f"0-{max_limit}"}
    elif parallel_runs == 'hybrid':
        # Multicore MPI x OpenMP runs
        nb_ranks = nb_nodes
        nb_threads = nb_cores_per_node
        mpi_affinity = {"I_MPI_PIN_DOMAIN":"auto:scatter"}
        omp_affinity = {"OMP_PLACES":"threads","OMP_PROC_BIND":"spread"}
    else:
        # Unicore runs
        nb_ranks = 1
        nb_threads = 1
        mpi_affinity = {"I_MPI_PIN_PROCESSOR_LIST":f"0-{max_limit}"}
        omp_affinity = {}

    # Invoque runner  per runtype
    compiler_run = run_app(app_env, binary, data_dir, run_dir, run_cmd, repetitions, runtype,
                           nb_ranks, nb_threads, mpi_affinity, omp_affinity, maqao_dir, ov_config)

    return (compiler_run,nb_ranks,nb_threads)
