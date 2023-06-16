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
import datetime
import argparse
import subprocess
import shutil
from utils.util import parse_env_map 
from base_runner import BaseRunner

LPROF_MAX_OVERHEAD = 1.03

class LProfRunner(BaseRunner):
    def __init__(self, run_dir_root, maqao_dir):
        super().__init__(maqao_dir)
        self.run_dir_root = run_dir_root
        self.run_dir_timestamp = int(round(datetime.datetime.now().timestamp()))
        self.run_dir = os.path.join(self.run_dir_root, f'run_{self.run_dir_timestamp}')
        self.lprof_time = 0

    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        true_run_cmd = run_cmd.replace('<binary>', binary_path)
        self.lprof_result_dir = os.path.join(self.run_dir, f'lprof_results')
        lprof_mpi_command = f"--mpi-command=\"{mpi_command}\"" if mpi_command else ""
        lprof_run_cmd=f'{self.maqao_dir}/bin/maqao lprof --mute {lprof_mpi_command} '\
            f'xp={self.lprof_result_dir} -- {true_run_cmd}'
        print(lprof_run_cmd)
        subprocess.run(lprof_run_cmd, shell=True, env=run_env, cwd=self.run_dir)
        return True

    def compute_lprof_time(self, lprof_walltime_script_path):
        run_cmd = f'{self.maqao_dir}/bin/maqao {lprof_walltime_script_path} {self.lprof_result_dir}'
        print(run_cmd)
        result = subprocess.run(run_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(result.stderr.decode("utf-8"))
            return 
        self.lprof_time = float(result.stdout.decode("utf-8"))
        print(self.lprof_time)

    def compute_lprof_overhead(self, reference_time):
        overhead = self.lprof_time / reference_time
        if overhead > LPROF_MAX_OVERHEAD:
            to_print = f'Lprof overhead: {overhead} is greater than {LPROF_MAX_OVERHEAD}\n' + \
                       f'Lprof sampling rate will be lowered'
            print(to_print)
            config = 'QAAS_LPROF_SAMPLING_RATE=\"sampling-rate=low\"'
            return config
        else:
            to_print = f'Lprof overhead: {overhead} is lower than {LPROF_MAX_OVERHEAD}\n' + \
                       f'Lprof sampling rate will be kept to default'
            print(to_print)
            return ''

# copy executable binary to current directory,
# copy data file to current directory,
# set up env map
# run command replacing <binary> by binary to executable binary
def exec(env, binary_path, maqao_path, run_dir, data_path, run_cmd, mode,
         mpi_run_command=None, mpi_num_processes=1, omp_num_threads=1, 
         mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=spread"}, omp_envs={}):
    lprof_runner = LProfRunner(run_dir, maqao_path)
    lprof_runner.exec (env, binary_path, data_path, run_cmd, mode, 
                     mpi_run_command, mpi_num_processes, omp_num_threads, 
                     mpi_envs, omp_envs)
    return lprof_runner
   
def build_argparser(parser, include_mode=True):
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--maqao-path', help='Path to maqao root', required=True)
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
