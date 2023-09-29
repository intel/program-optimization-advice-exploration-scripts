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

import datetime
import os
from logger import log, QaasComponents
import argparse
import subprocess
from utils.util import generate_timestamp_str
from base_runner import BaseRunner
script_dir=os.path.dirname(os.path.realpath(__file__))

# TODO: refactor with Profiler.py
class OneviewRunner(BaseRunner):
    #MAQAO_DIR="/nfs/site/proj/alac/software/UvsqTools/20221102"
    ONEVIEW_OUT_DIR='oneview_out_dir'

    def __init__(self, maqao_dir, level, ov_result_root, ov_config, ov_of):
        super().__init__(maqao_dir)
        self.level = level
        self.ov_result_root = ov_result_root
        self.ov_config = ov_config
        self.ov_timestamp = int(round(datetime.datetime.now().timestamp()))
        self.run_dir = os.path.join(self.ov_result_root, f'oneview_run_{self.ov_timestamp}')
        self.ov_of = ov_of

    @property
    def maqao_bin_dir(self):
        return os.path.join(self.maqao_dir, 'bin')

    @property
    def maqao_lib_dir(self):
        return os.path.join(self.maqao_dir, 'lib')
        
    @property
    def maqao_bin(self):
        return os.path.join(self.maqao_bin_dir, 'maqao')

    def format_ov_shared_libs_option(self, so_libs):
        '''Convert shared libs paths to OV format.'''
        return ','.join(['\\"'+str(item) + '\\"' for item in so_libs])

    def extract_flops_count(self):
        '''Get Flops count from OV report'''
        # Extract lprof computed GFlops number
        result = subprocess.run(f"grep GFlops global_metrics.csv  | cut -d';' -f3", shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=os.path.join(self.ov_result_dir, 'shared', 'run_0'))
        gflops = float(result.stdout.decode('utf-8'))
        # Extract lprof wall clock time
        result = subprocess.run(f"tail -n 1 expert_run.csv | cut -d';' -f1", shell=True, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=os.path.join(self.ov_result_dir, 'shared', 'run_0'))
        time = float(result.stdout.decode('utf-8'))
        # Return number of operations (Flops)
        return gflops * time

    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        true_run_cmd = run_cmd.replace('<binary>', binary_path)
        pinning_cmd = "" if mpi_command else f"--pinning-command=\"{self.get_pinning_cmd()}\""

        self.ov_result_dir = os.path.join(self.ov_result_root, f'oneview_results_{self.ov_timestamp}')
        os.makedirs(self.ov_result_dir)

        ov_mpi_command = f"--mpi-command=\"{mpi_command}\"" if mpi_command else ""
        ov_filter_option = '--filter="{type=\\\"number\\\", value=4}"' if self.level != 1 else ''
        ov_extra_libs_option = '--external-libraries="{' + self.format_ov_shared_libs_option(self.found_so_libs) + '}"' if self.found_so_libs else ""

        ov_run_cmd=f'{self.maqao_bin} oneview -R{self.level} {ov_mpi_command} '\
            f' --with-FLOPS ' \
            f' {ov_extra_libs_option} '\
            f'--run-directory="{run_dir}" {pinning_cmd} '\
            f'--replace xp={self.ov_result_dir} '\
            f'{ov_filter_option} '\
            f'-of={self.ov_of} '\
            f'-- {true_run_cmd}'
        print(ov_run_cmd)
        print(self.ov_result_dir)
        run_env["LD_LIBRARY_PATH"] = run_env.get("LD_LIBRARY_PATH") + ":" + self.maqao_lib_dir
        result = subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True

        print(f"OneView Level {self.level} failed! Fallback to lower level")
        new_level = self.level - 1
        if new_level == 0:
            return False
        ov_run_cmd = ov_run_cmd.replace(f"-R{self.level}", "-R{new_level}")
        self.level = new_level
        print(ov_run_cmd)
        result = subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True

        print(f"OneView Level {self.level} failed! Fallback to lower level")
        new_level = self.level - 1
        if new_level == 0:
            return False
        ov_run_cmd = ov_run_cmd.replace(f"-R{self.level}", "-R{new_level}")
        self.level = new_level
        print(ov_run_cmd)
        result = subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        else:
            return False

def exec(env, binary_path, data_path, ov_result_root, run_cmd, maqao_path, ov_config, mode, 
             level=1, mpi_run_command=None, mpi_num_processes=1, omp_num_threads=1, 
             mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=spread"}, omp_envs={}, ov_of="html"):
    ov_runner = OneviewRunner(maqao_dir=maqao_path, level=level, ov_result_root=ov_result_root, ov_config=ov_config, ov_of=ov_of)
    success = ov_runner.exec (env, binary_path, data_path, run_cmd, mode, mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs)
    if success:
        log(QaasComponents.OV_RUNNER, f'Result at {ov_runner.ov_result_dir}', mockup=False)
        return ov_runner
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="Testing loop time aggregation")
    parser.add_argument('--run-path', help='Path to run directory', required=True)
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--src-file', help='Loop source file', required=True)
    parser.add_argument('--loop-line-num', help='Loop head line number', required=True, type=int)
    args = parser.parse_args()
    pass

if __name__ == "__main__": 
    main()
