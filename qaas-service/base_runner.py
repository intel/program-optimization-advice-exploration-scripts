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
import shutil
import pathlib
from abc import ABC, abstractmethod
from utils.runcmd import QAASRunCMD

class BaseRunner(ABC):
    def __init__(self, maqao_dir):
        self._maqao_dir = maqao_dir
    
    @property
    def maqao_dir(self):
        return self._maqao_dir

    def prepare(self, binary_path, data_path):
        os.makedirs(self.run_dir, exist_ok=True)
        try:
            os.symlink(binary_path, os.path.join(self.run_dir, os.path.basename(binary_path)))
        except:
            pass
        try:
            if os.path.isfile(data_path):
                os.symlink(data_path, os.path.join(self.run_dir, data_path))
            else:
                assert os.path.isdir(data_path)
                for file in os.listdir(data_path): 
                    os.symlink(os.path.join(data_path, file), os.path.join(self.run_dir, file))
        except:
            pass

    def search_shared_libs(self, build_dir):
        '''Search all shared libraries (*.so) generated after build.'''
        return list(pathlib.Path(build_dir).glob('**/*.so*'))

    def find_shared_libs_location(self, so_libs):
        '''Find shared libs location.'''
        return ':'.join(list(set([os.path.dirname(item) for item in so_libs])))

    def run(self, binary_path, run_cmd, 
            mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs, env):
        run_env = env.copy()
        run_env.update(mpi_envs)
        run_env.update(omp_envs)
        run_env["OMP_NUM_THREADS"] = str(omp_num_threads)
        mpi_command = f"{mpi_run_command} -np {mpi_num_processes}" if mpi_run_command else ""
        # Setup LD_LIBRARY_PATH with any found shared libraries built by cmake
        self.found_so_libs = self.search_shared_libs(run_env['QAAS_BUILD_DIR'])
        run_env["LD_LIBRARY_PATH"] = run_env.get("LD_LIBRARY_PATH") + ":" + self.find_shared_libs_location(self.found_so_libs)
        success = self.true_run(binary_path, self.run_dir, run_cmd, run_env, mpi_command)
        return success

    # Subclass override to do the real run
    @abstractmethod
    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        pass

    def exec(self, env, binary_path, data_path, run_cmd, mode,
             mpi_run_command, mpi_num_processes, omp_num_threads, 
             mpi_envs, omp_envs):
        success = True
        if mode == 'prepare' or mode == 'both':
            self.prepare(binary_path, data_path)

        if mode == 'run' or mode == 'both':
           success = self.run(binary_path, run_cmd, 
                     mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs, env)
        return success

    def pin_seq_run_cmd(self, run_cmd):
        pinning_cmd = self.get_pinning_cmd()

        seq_run_cmd = f'{pinning_cmd} {run_cmd}'
        return seq_run_cmd

    def get_pinning_cmd(self):
        last_node, last_core = get_last_core_and_node()
        pinning_cmd = f'/usr/bin/numactl -m {last_node} -C {last_core}'
        return pinning_cmd

def get_last_core_and_node():
    rc, cmdout = QAASRunCMD(0).run_local_cmd("/usr/bin/numactl -H | awk '/cpus/ && $2>=max {max=$2}; END{print max}'")
    last_node = int(cmdout)
    rc, cmdout = QAASRunCMD(0).run_local_cmd(f"/usr/bin/numactl -H | grep 'node {last_node}' | grep  'cpus' |cut -d: -f2|xargs -n1|sort -r -n|head -1")
    last_core = int(cmdout)
    return last_node,last_core
