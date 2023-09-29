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
# Contributors: Hafid/David

from argparse import ArgumentParser
import subprocess
import os
import sys
import resource

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
from qaas_logic_initial_profile import run_initial_profile
from qaas_logic_compile import compile_binaries as compile_all
from qaas_logic_unicore import run_qaas_UP
from qaas_logic_multicore import run_qaas_MP

def run_demo_phase(to_backplane, src_dir, data_dir, ov_config, ov_run_dir, locus_run_root, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags):
    ov_run_dir_orig = os.path.join(ov_run_dir, 'orig')
    orig_binary = os.path.join(ov_run_dir_orig, 'exec')
    to_backplane.send(qm.GeneralStatus("Start Building orig app"))
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                  orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                  user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)
    to_backplane.send(qm.GeneralStatus("Done Building orig app"))
    to_backplane.send(qm.GeneralStatus("Start Running orig app"))
    oneview_runner.exec(app_builder_env, orig_binary, data_dir, ov_run_dir_orig, run_cmd, maqao_dir, ov_config, 'both')
    to_backplane.send(qm.GeneralStatus("Done Running orig app"))
    ov_run_dir_opt = os.path.join(ov_run_dir, 'opt')
    opt_binary = os.path.join(ov_run_dir_opt, 'exec')
    to_backplane.send(qm.GeneralStatus("Start Tuning orig app"))
    mutator_env = app_mutator.exec(locus_run_root, src_dir, compiler_dir, maqao_dir, opt_binary, orig_user_CC, target_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
         data_dir, run_cmd, env_var_map, user_target_location) 
    to_backplane.send(qm.GeneralStatus("Done Tuning orig app"))
    to_backplane.send(qm.GeneralStatus("Start Running tuned app"))
    oneview_runner.exec(mutator_env, opt_binary, data_dir, ov_run_dir_opt, run_cmd, maqao_dir, ov_config, 'both')
    to_backplane.send(qm.GeneralStatus("Done Running tuned app"))

def run_multiple_phase(to_backplane, src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, locus_run_root, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags,
                     disable_compiler_default, disable_compiler_flags, parallel_compiler_runs):
    '''QAAS Ruuning Logic/Strategizer Entry Point.''' 

    print(parallel_compiler_runs)
    # Increase stack size soft limit for the current process and children
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY,-1))
    # Setup QaaS reports dir
    qaas_reports_dir = os.path.join(os.path.dirname(base_run_dir), 'qaas_reports')

    # Phase 2: Intial profiling and cleaning    
    to_backplane.send(qm.GeneralStatus("QAAS running logic: Initail Profiling and Cleaning"))
    rc,msg,defaults,flops = run_initial_profile(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, 
                     run_cmd, env_var_map, extra_cmake_flags, qaas_reports_dir, 
                     disable_compiler_default, parallel_compiler_runs)
    if rc != 0: 
        to_backplane.send(qm.GeneralStatus(msg))
        return
    to_backplane.send(qm.GeneralStatus("Done Initail Profiling and Cleaning!"))
    print(defaults)

    # Phase 3.1: Parameter Exploration and Tuning

    # First build all options
    binaries_dir = os.path.join(os.path.dirname(base_run_dir), 'binaries')
    compiled_options = compile_all(src_dir, binaries_dir, compiler_dir,
                orig_user_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                user_link_flags, user_target, user_target_location, extra_cmake_flags, env_var_map)
    to_backplane.send(qm.GeneralStatus("Done compile all binaries!"))

    if not disable_compiler_flags:
        # First build all options
        binaries_dir = os.path.join(os.path.dirname(base_run_dir), 'binaries')
        compiled_options = compile_all(src_dir, binaries_dir, compiler_dir,
                    orig_user_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                    user_link_flags, user_target, user_target_location, extra_cmake_flags, env_var_map)
        to_backplane.send(qm.GeneralStatus("Done compile all binaries!"))
    
        # Start unicore runs
        to_backplane.send(qm.GeneralStatus("QAAS running logic: Compilers Parameters Exploration/Tuning"))
        rc,msg = run_qaas_UP(user_target, src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                         orig_user_CC, run_cmd, compiled_options, qaas_reports_dir, defaults, flops, parallel_compiler_runs)
        if rc != 0: 
            to_backplane.send(qm.GeneralStatus(msg))
            return
        to_backplane.send(qm.GeneralStatus("Done Compilers Parameters Exploration/Tuning!"))

    # Start multicore runs
    to_backplane.send(qm.GeneralStatus("QAAS running logic: Multicore Parameters Exploration/Tuning"))
    rc,qaas_best_opt,msg = run_qaas_MP(user_target, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                     orig_user_CC, run_cmd, compiled_options, qaas_best_opt, qaas_reports_dir)
    if rc != 0:
        to_backplane.send(qm.GeneralStatus(msg))
        return
    to_backplane.send(qm.GeneralStatus("Done Unicore Parameters Exploration/Tuning!"))
    return

if __name__ == '__main__':
    parser = ArgumentParser(description='Run a job at the machine in a container.')
    parser.add_argument('--data_dir', nargs='?', required=True) 
    parser.add_argument('--base_run_dir', nargs='?', default="")
    parser.add_argument('--ov_dir', nargs='?', required=True)
    parser.add_argument('--ov_config', nargs='?', required=True)
    parser.add_argument('--ov_run_dir', nargs='?', required=True)
    parser.add_argument('--locus_run_dir', nargs='?', required=True)
    parser.add_argument('--run-cmd', help='Command to run of the form ... <binary> ... where <binary> represent the executable', required=True)
    parser.add_argument('--var', help='Env variable to add', required=False, action='append')
    parser.add_argument('--comm-port', nargs='?', type=int, default=None) 
    parser.add_argument('--logic', help='Select the QaaS run strategy', choices=['demo', 'strategizer'], default='demo')
    parser.add_argument('--no-compiler-default', action="store_true", help="Disable search for best default compiler", required=False)
    parser.add_argument('--no-compiler-flags', action="store_true", help="Disable search for best compiler flags", required=False)
    parser.add_argument('-p', '--parallel-compiler-runs', choices=['off', 'mpi', 'openmp', 'hybrid'], default='off',
                               help="Force multiprocessing [MPI, OpenMP or hybrid] for compiler search runs")
    app_builder_builder_argparser(parser, include_binary_path=False, include_mode=False)
    args = parser.parse_args()
    log(QaasComponents.BUSINESS_LOGICS, 'Executing job.py script in a container', mockup=True)

    env_var_map = parse_env_map(args)
    
    to_backplane = ServiceMessageSender(args.comm_port)
    to_backplane.send(qm.BeginJob())
    if args.logic == "demo":
        run_demo_phase(to_backplane, args.src_dir, args.data_dir, args.ov_config, args.ov_run_dir, args.locus_run_dir, args.compiler_dir, args.ov_dir,
                     args.orig_user_CC, args.target_CC, args.user_c_flags, args.user_cxx_flags, args.user_fc_flags,
                     args.user_link_flags, args.user_target, args.user_target_location, args.run_cmd, env_var_map, args.extra_cmake_flags)
    else:
        run_multiple_phase(to_backplane, args.src_dir, args.data_dir, args.base_run_dir, args.ov_config, args.ov_run_dir, args.locus_run_dir, args.compiler_dir, args.ov_dir,
                     args.orig_user_CC, args.target_CC, args.user_c_flags, args.user_cxx_flags, args.user_fc_flags,
                     args.user_link_flags, args.user_target, args.user_target_location, args.run_cmd, env_var_map, args.extra_cmake_flags,
                     args.no_compiler_default, args.no_compiler_flags, args.parallel_compiler_runs)
    to_backplane.send(qm.EndJob())
    to_backplane.close()
