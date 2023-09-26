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
import time
import datetime
import argparse
import subprocess
import shutil
from statistics import mean
from statistics import median
from utils.util import parse_env_map 
from base_runner import BaseRunner

class AppRunner(BaseRunner):
    def __init__(self, run_dir_root, meta_repetitions=1, maqao_dir=None):
        super().__init__(maqao_dir)
        self.run_dir_root = run_dir_root
        self.run_dir_timestamp = int(round(datetime.datetime.now().timestamp()))
        self.run_dir = os.path.join(self.run_dir_root, f'run_{self.run_dir_timestamp}')
        self.meta_repetitions = meta_repetitions
        self.exec_times = []

    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        true_run_cmd = run_cmd.replace('<binary>', binary_path)
        pinning_cmd = "" if mpi_command else f"{self.get_pinning_cmd()}"
        base_run_cmd=f'{mpi_command} {true_run_cmd}' if mpi_command else f'{pinning_cmd} {true_run_cmd}'
        print(f"run_dir is: {run_dir}")
        print(base_run_cmd)
        for i in range(self.meta_repetitions):
            subprocess.run(f"echo run:{i} > runs.log", shell=True, cwd=self.run_dir)
            start = time.time_ns()
            result = subprocess.run(f"{base_run_cmd} >> output.out 2>&1", shell=True, env=run_env, cwd=self.run_dir)
            stop = time.time_ns()
            if result.returncode != 0:
                print(f"Check errors in {self.run_dir}/output.out")
                return False
            self.exec_times.append((stop - start)/1e9)

        return True

    def compute_min_exec_time(self):
        value = None
        if len(self.exec_times) == self.meta_repetitions:
            value = min(self.exec_times)
        return value

    def compute_mean_exec_time(self):
        value = None
        if len(self.exec_times) == self.meta_repetitions:
            value = mean(self.exec_times)
        return value

    def compute_median_exec_time(self):
        value = None
        if len(self.exec_times) == self.meta_repetitions:
            value = median(self.exec_times)
        return value

    def compute_stability_metric(self):
        stability = None
        if len(self.exec_times) == self.meta_repetitions:
            min_value = self.compute_min_exec_time()
            med_value = self.compute_median_exec_time()
            stability = (med_value - min_value)/min_value*100
        return stability

# copy executable binary to current directory,
# copy data file to current directory,
# set up env map
# run command replacing <binary> by binary to executable binary
def exec(env, binary_path, data_path, run_dir, run_cmd, mode, repetitions=1,
         mpi_run_command=None, mpi_num_processes=1, omp_num_threads=1, 
         mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=spread"}, omp_envs={}):
    app_runner = AppRunner(run_dir, repetitions)
    app_runner.exec (env, binary_path, data_path, run_cmd, mode, 
                     mpi_run_command, mpi_num_processes, omp_num_threads, 
                     mpi_envs, omp_envs)
    return app_runner
   
def build_argparser(parser, include_mode=True):
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--run-dir', help='Path to directory to run executable', required=True)
    parser.add_argument('--data-path', help='Path to data file', required=True)
    parser.add_argument('--var', help='Env variable to add', required=False, action='append')
    parser.add_argument('--run-cmd', help='Command to run of the form ... <binary> ... where <binary> represent the executable', required=True)
    if include_mode:
        parser.add_argument('--mode', help='Mode of run', choices=['prepare', 'run', 'both'], required=True)
    #parser.add_argument('--compiler-dir', help='Path to compiler', required=True)

def main():
    parser = argparse.ArgumentParser(description="Run application")
    build_argparser(parser)
    args = parser.parse_args()
    env_var_map = parse_env_map(args)
    my_env = os.environ.copy()
    my_env.update(env_var_map)
    exec(my_env, args.binary_path, args.maqao_path, args.run_dir, args.data_path, args.run_cmd, args.mode)

if __name__ == "__main__": 
    main()
