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
import time

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
from utils.system import increase_run_resources_limits
from qaas_logic_initial_profile import run_initial_profile
from qaas_logic_compile import compile_binaries as compile_all
from qaas_logic_unicore import run_qaas_UP
from qaas_logic_multicore import run_qaas_MP
from qaas_metadata import QAASMetaDATA
import traceback

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
                     disable_compiler_default, disable_compiler_flags, parallel_compiler_runs, runtime, multi_compilers_dirs):
    '''QAAS Ruuning Logic/Strategizer Entry Point.'''

    # Increase run resources limits
    increase_run_resources_limits()
    # Setup QaaS reports dir
    qaas_reports_dir = os.path.join(os.path.dirname(base_run_dir), 'qaas_reports')

    # Dump meta data file
    qaas_meta = QAASMetaDATA(qaas_reports_dir)
    qaas_meta.add_qaas_metadata(run_cmd)
    qaas_meta.add_system_metadata(maqao_dir)
    for compiler in multi_compilers_dirs:
        qaas_meta.add_compiler_version(compiler, multi_compilers_dirs[compiler])
    qaas_meta.add_mpi_version(compiler_dir)
    # Dispatch MPI provider inforation to all runs
    env_var_map['MPI_PROVIDER'] = qaas_meta.config['SYSTEM']["mpi_provider"]

    # Overide MPI wrapper depending on loaded environment
    orig_user_CC = orig_user_CC.replace('MPI-', 'mpiicc-') if env_var_map['MPI_PROVIDER'] == 'IntelMPI' else orig_user_CC.replace('MPI-', 'mpicc-')
    target_CC = target_CC.replace('MPI-', 'mpiicc-') if env_var_map['MPI_PROVIDER'] == 'IntelMPI' else target_CC.replace('MPI-', 'mpicc-')

    # Phase 2: Intial profiling and cleaning
    start = time.time()
    to_backplane.send(qm.GeneralStatus("QAAS running logic: Initail Profiling and Cleaning"))
    rc,msg,defaults,flops,nb_mpi,nb_omp,defaults_envs = run_initial_profile(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location,
                     run_cmd, env_var_map, extra_cmake_flags, qaas_reports_dir,
                     disable_compiler_default, parallel_compiler_runs, multi_compilers_dirs)
    stop = time.time()
    QAASMetaDATA(qaas_reports_dir).add_qaas_logic_timings("initial_profile", int(stop - start))
    if rc != 0:
        to_backplane.send(qm.GeneralStatus(msg))
        return
    to_backplane.send(qm.GeneralStatus("Done Initail Profiling and Cleaning!"))

    # Phase 3.1: Parameter Exploration and Tuning
    if not disable_compiler_flags:
        # First build all options
        binaries_dir = os.path.join(os.path.dirname(base_run_dir), 'binaries')
        start = time.time()
        compiled_options = compile_all(src_dir, binaries_dir, compiler_dir,
                    orig_user_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                    user_link_flags, user_target, user_target_location, extra_cmake_flags, env_var_map, multi_compilers_dirs, maqao_dir)
        stop = time.time()
        if compiled_options == None:
            to_backplane.send(qm.GeneralStatus('Unknown CPU Vendor or Micro Architecture'))
            return
        QAASMetaDATA(qaas_reports_dir).add_qaas_logic_timings("build_binaries", int(stop - start))
        to_backplane.send(qm.GeneralStatus("Done compile all binaries!"))

        # Start unicore runs
        to_backplane.send(qm.GeneralStatus("QAAS running logic: Compilers Parameters Exploration/Tuning"))
        start = time.time()
        rc,compile_best_opt,bestcomp,msg = run_qaas_UP(user_target, src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                         orig_user_CC, run_cmd, compiled_options, qaas_reports_dir, defaults, flops, parallel_compiler_runs)
        stop = time.time()
        QAASMetaDATA(qaas_reports_dir).add_qaas_logic_timings("multicompiler", int(stop - start))
        if rc != 0:
            to_backplane.send(qm.GeneralStatus(msg))
            return
        to_backplane.send(qm.GeneralStatus("Done Compilers Parameters Exploration/Tuning!"))
    else:
        compiled_options = {}
        compile_best_opt = {}
        bestcomp = ''

    # Generate m-compiler OV compare report
    ov_run = oneview_runner.OneviewRunner(maqao_dir, 1, ov_run_dir, None, None)
    ov_run.generate_mcompiler_html_compare_report(qaas_reports_dir)

    # Start multicore runs
    if runtime["enable_scale"]:
        to_backplane.send(qm.GeneralStatus("QAAS running logic: Multicore Parameters Exploration/Tuning"))
        # Get scaling mode
        has_mpi = True if runtime['mpi'] != 'no' else False
        has_omp = True if runtime['openmp'] != 'no' else False
        mpi_weak = True if runtime['mpi'] == 'weak' else False
        omp_weak = True if runtime['openmp'] == 'weak' else False

        # Dump meta data file (scaling modes)
        qaas_meta = QAASMetaDATA(qaas_reports_dir)
        qaas_meta.add_scalability_metadata(runtime['mpi'], runtime['openmp'])

        # Compute flops
        if mpi_weak and omp_weak:
            # App has MPI and OpenMP and both scale through replication
            flops_per_app = flops/(nb_mpi * nb_omp)
        elif mpi_weak and (not has_omp or not omp_weak):
            # App implements replication through MPI only
            flops_per_app = flops/nb_mpi
        elif omp_weak and (not has_mpi or not mpi_weak):
            # App implements replication through OpenMP only
            flops_per_app = flops/nb_omp
        else:
            # App implements classic strong scaling: FLOPS is invariant
            flops_per_app = flops

        # Add #MPI and #OMP used for compiler exploration to bestcomp options
        #compile_best_opt["MPI"] = nb_mpi
        #compile_best_opt["OMP"] = nb_omp

        # Reconstruct what to run
        defaults[defaults_envs['orig']] = defaults['orig']
        consolidated_options = {}
        new_best_opt = {}
        min_time = 0.0
        for compiler in defaults.keys():
            if compiler  == 'orig' or defaults[compiler] == None or defaults[compiler] == 0.0:
                continue
            new_best_opt[compiler] = {'index':-1, 'time':defaults[compiler],'build':compiler}
            consolidated_options[compiler] = defaults_envs[compiler]
            if min_time == 0.0 or defaults[compiler] < min_time:
                min_time = defaults[compiler]
                bestcomp = compiler
        for compiler in compile_best_opt.keys():
            if compile_best_opt[compiler]['time'] == None or compile_best_opt[compiler]['time'] == 0.0:
                continue
            if compiler in new_best_opt and compile_best_opt[compiler]['time'] >= defaults[compiler]:
                continue
            else:
                new_best_opt[compiler] = compile_best_opt[compiler]
                consolidated_options[compiler] = compiled_options[compiler]
            if min_time == 0.0 or compile_best_opt[compiler]['time'] < min_time:
                min_time = compile_best_opt[compiler]['time']
                bestcomp = compiler

        # Add #MPI and #OMP used for compiler exploration to bestcomp options
        new_best_opt["MPI"] = nb_mpi
        new_best_opt["OMP"] = nb_omp

        # Run scalability
        start = time.time()
        rc,mp_best_opt,msg = run_qaas_MP(user_target, data_dir, base_run_dir, ov_config, ov_run_dir, maqao_dir,
                     orig_user_CC, run_cmd, consolidated_options, new_best_opt, bestcomp, qaas_reports_dir,
                     has_mpi, has_omp, mpi_weak, omp_weak, flops_per_app, runtime['scale_bestcomp'])
        stop = time.time()
        QAASMetaDATA(qaas_reports_dir).add_qaas_logic_timings("scalability", int(stop - start))
        if rc != 0:
            to_backplane.send(qm.GeneralStatus(msg))
            return
        to_backplane.send(qm.GeneralStatus("Done Unicore Parameters Exploration/Tuning!"))

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
    parser.add_argument('--logic', help='Select the QaaS run strategy', choices=['demo', 'strategizer'], default='strategizer')
    parser.add_argument('--no-compiler-default', action="store_true", help="Disable search for best default compiler", required=False)
    parser.add_argument('--no-compiler-flags', action="store_true", help="Disable search for best compiler flags", required=False)
    parser.add_argument('-p', '--parallel-compiler-runs', choices=['auto', 'off', 'mpi', 'openmp', 'hybrid'], default='auto',
                               help="Force multiprocessing [auto, MPI, OpenMP or hybrid] for compiler search runs")
    parser.add_argument('-s', '--enable-scale', action="store_true", help="Turn on multicore scalability runs", required=False)
    parser.add_argument('--enable-scale-on-best-compiler', dest='scale_bestcomp',  action="store_true", help="Scalability runs only best compiler", required=False)
    parser.add_argument('--mpi-scale-type', help='MPI scaling type', choices=['strong', 'weak', 'no'], default='strong')
    parser.add_argument('--openmp-scale-type', help='OpenMP scaling type', choices=['strong', 'weak', 'no'], default='strong')
    parser.add_argument('--multi-compilers_dirs', nargs='?', required=False, default='')
    app_builder_builder_argparser(parser, include_binary_path=False, include_mode=False)
    args = parser.parse_args()
    log(QaasComponents.BUSINESS_LOGICS, 'Executing job.py script in a container', mockup=True)
    # Prepare env variables
    env_var_map = parse_env_map(args)
    # Prepare parallel runtime scaling modes
    runtime = {'enable_scale':args.enable_scale, 'scale_bestcomp':args.scale_bestcomp, 'mpi':args.mpi_scale_type, 'openmp':args.openmp_scale_type}
    # Set default m-compiler to m-core mode
    if args.parallel_compiler_runs != 'auto':
        parallel_compiler_runs = args.parallel_compiler_runs
    else:
        if runtime['mpi'] != 'no' and runtime['openmp'] != 'no':
            parallel_compiler_runs = 'hybrid'
        elif runtime['mpi'] != 'no':
            parallel_compiler_runs = 'mpi'
        elif runtime['openmp'] != 'no':
            parallel_compiler_runs = 'openmp'
        else:
            parallel_compiler_runs = 'off'
    # Put compiler:compiler_dir into a dict
    multi_compilers_dirs = {}
    if not args.multi_compilers_dirs == "":
        for item in args.multi_compilers_dirs.split(';'):
            compiler,path = item.split(':')
            multi_compilers_dirs[compiler] = path

    to_backplane = ServiceMessageSender(args.comm_port)
    to_backplane.send(qm.BeginJob())
    rc = 0
    try:
        if args.logic == "demo":
            run_demo_phase(to_backplane, args.src_dir, args.data_dir, args.ov_config, args.ov_run_dir, args.locus_run_dir, args.compiler_dir, args.ov_dir,
                        args.orig_user_CC, args.target_CC, args.user_c_flags, args.user_cxx_flags, args.user_fc_flags,
                        args.user_link_flags, args.user_target, args.user_target_location, args.run_cmd, env_var_map, args.extra_cmake_flags)
        else:
            run_multiple_phase(to_backplane, args.src_dir, args.data_dir, args.base_run_dir, args.ov_config, args.ov_run_dir, args.locus_run_dir, args.compiler_dir, args.ov_dir,
                        args.orig_user_CC, args.target_CC, args.user_c_flags, args.user_cxx_flags, args.user_fc_flags,
                        args.user_link_flags, args.user_target, args.user_target_location, args.run_cmd, env_var_map, args.extra_cmake_flags,
                        args.no_compiler_default, args.no_compiler_flags, parallel_compiler_runs, runtime, multi_compilers_dirs)
    except Exception as e:
        to_backplane.send(qm.GeneralStatus(str(e)))
        #traceback.print_tb(e.__traceback__)
        traceback.print_exc()
        rc = -1
    to_backplane.send(qm.EndJob())
    to_backplane.close()
    exit(rc)
