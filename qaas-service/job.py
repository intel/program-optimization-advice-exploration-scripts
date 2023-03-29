# Contributors: Hafid/David
from argparse import ArgumentParser
import subprocess
import os
import sys

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

this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
script_name=os.path.basename(os.path.realpath(__file__))

LPROF_WALLTIME_LUA_FILE=os.path.join(script_dir, 'lua_scripts', 'lprof_walltime.lua')

DEFAULT_REPETITIONS = 11
MAX_ALLOWED_EXEC_TIME = 180

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

def run_multiple_phase(to_backplane, src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, locus_run_root, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags):
    base_run_dir_orig = os.path.join(base_run_dir, 'orig')
    orig_binary = os.path.join(base_run_dir_orig, 'exec')
    to_backplane.send(qm.GeneralStatus("Start Building orig app"))
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)
    to_backplane.send(qm.GeneralStatus("Done Building orig app"))

    to_backplane.send(qm.GeneralStatus("Start Phase 2: INITIAL PROFILING"))
    to_backplane.send(qm.GeneralStatus("Start S2.1"))
    basic_run = app_runner.exec(app_builder_env, orig_binary, data_dir, base_run_dir_orig, run_cmd, 'both', DEFAULT_REPETITIONS, "mpirun")
    print(basic_run.exec_times)
    tmp = [str(x) for x in basic_run.exec_times]
    to_backplane.send(qm.GeneralStatus(f"Exec time: {tmp}"))
    stability = basic_run.compute_stability_metric()
    new_repetitions = compute_repetitions(stability)
    if new_repetitions < 1:
        return
    median_value = basic_run.compute_median_exec_time()
    if median_value > MAX_ALLOWED_EXEC_TIME:
        to_backplane.send(qm.GeneralStatus(f"ABORT: median execution time {median_value} greater than allowed {MAX_ALLOWED_EXEC_TIME}"))
        return
    to_backplane.send(qm.GeneralStatus("Done S2.1"))

    to_backplane.send(qm.GeneralStatus("Start S2.2"))
    lprof_run = lprof_runner.exec(app_builder_env, orig_binary, maqao_dir, base_run_dir_orig, data_dir, run_cmd, 'both', "mpirun", 1)
    lprof_run.compute_lprof_time(LPROF_WALLTIME_LUA_FILE)
    new_lprof_conf = lprof_run.compute_lprof_overhead(median_value)
    print(new_lprof_conf)
    to_backplane.send(qm.GeneralStatus("Done S2.2"))

    to_backplane.send(qm.GeneralStatus("Start S2.3"))
    print("add more flags")
    ov_run_dir_orig = os.path.join(ov_run_dir, 'orig')
    oneview_runner.exec(app_builder_env, orig_binary, data_dir, ov_run_dir_orig, run_cmd, maqao_dir, ov_config, 'both', level=1, mpi_run_command="mpirun", mpi_num_processes=1)
    orig_binary = os.path.join(ov_run_dir_orig, 'exec')
    update_c_flags = f"{user_c_flags} -g -grecord-command-line -fno-omit-frame-pointer" if user_c_flags else "" 
    update_cxx_flags = f"{user_cxx_flags} -g -grecord-command-line -fno-omit-frame-pointer" if user_cxx_flags else "" 
    update_fc_flags = f"{user_fc_flags} -g -grecord-command-line -fno-omit-frame-pointer" if user_fc_flags else "" 
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, update_c_flags, update_cxx_flags, update_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)
    to_backplane.send(qm.GeneralStatus("Done S2.3"))

    to_backplane.send(qm.GeneralStatus("Start S2.4"))
    oneview_runner.exec(app_builder_env, orig_binary, data_dir, ov_run_dir_orig, run_cmd, maqao_dir, ov_config, 'both', level=1, mpi_run_command="mpirun", mpi_num_processes=1)
    to_backplane.send(qm.GeneralStatus("Done S2.4"))

    to_backplane.send(qm.GeneralStatus("Start S2.5"))
    print("Check performance anomalies like I/O time")
    to_backplane.send(qm.GeneralStatus("Done S2.5"))
    to_backplane.send(qm.GeneralStatus("Done Phase 2: INITIAL PROFILING"))
    return

    to_backplane.send(qm.GeneralStatus("Start Phase 3: PARAMETER EXPLORATION/TUNING"))
    to_backplane.send(qm.GeneralStatus("Start UP1"))
    to_backplane.send(qm.GeneralStatus("Done UP1"))

    to_backplane.send(qm.GeneralStatus("Start UP2"))
    to_backplane.send(qm.GeneralStatus("Done UP2"))

    to_backplane.send(qm.GeneralStatus("Start UP3O"))
    to_backplane.send(qm.GeneralStatus("Done UP3O"))

    to_backplane.send(qm.GeneralStatus("Start UP4O"))
    to_backplane.send(qm.GeneralStatus("Done UP4O"))
    to_backplane.send(qm.GeneralStatus("Done Phase 3: PARAMETER EXPLORATION/TUNING"))

    to_backplane.send(qm.GeneralStatus("Start UP"))
    to_backplane.send(qm.GeneralStatus("Done UP"))

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
                     args.user_link_flags, args.user_target, args.user_target_location, args.run_cmd, env_var_map, args.extra_cmake_flags)
    to_backplane.send(qm.EndJob())
    to_backplane.close()
