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

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))
LPROF_WALLTIME_LUA_FILE=os.path.join(script_dir, 'lua_scripts', 'lprof_walltime.lua')

DEFAULT_REPETITIONS = 11
MAX_ALLOWED_EXEC_TIME = 180

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

def run_initial_profile(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags):
    ''' Execute QAAS Running Logic: INITIAL PROFILING AND CLEANING'''

    # Setup binary
    base_run_dir_orig = os.path.join(base_run_dir, 'orig')
    orig_binary = os.path.join(base_run_dir_orig, 'exec')

    # Build originl app using user-provided compilation options
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)

    # Setup run directory and launch initial run
    basic_run = app_runner.exec(app_builder_env, orig_binary, data_dir, base_run_dir_orig, run_cmd, 'both', DEFAULT_REPETITIONS, "mpirun")
    print(basic_run.exec_times)
    tmp = [str(x) for x in basic_run.exec_times]
    #to_backplane.send(qm.GeneralStatus(f"Exec time: {tmp}"))

    # Check performance stability
    stability = basic_run.compute_stability_metric()
    new_repetitions = compute_repetitions(stability)
    if new_repetitions < 1:
        rc=-1
        error_msg='Stop profiling: execution times instable!'
        return rc,error_msg,0

    # Check execution in defined range
    median_value = basic_run.compute_median_exec_time()
    if median_value > MAX_ALLOWED_EXEC_TIME:
        rc=-1
        error_msg=f"ABORT: median execution time {median_value} greater than allowed {MAX_ALLOWED_EXEC_TIME}"
        return rc,error_msg,0

    # Check LProf overhead
    lprof_run = lprof_runner.exec(app_builder_env, orig_binary, maqao_dir, base_run_dir_orig, data_dir, run_cmd, 'both', "mpirun", 1)
    lprof_run.compute_lprof_time(LPROF_WALLTIME_LUA_FILE)
    new_lprof_conf = lprof_run.compute_lprof_overhead(median_value)
    print(new_lprof_conf)

    # Add debug compilation flags and rebuild app
    ov_run_dir_orig = os.path.join(ov_run_dir, 'orig')
    orig_binary = os.path.join(ov_run_dir_orig, 'exec')
    update_c_flags = f"{user_c_flags} -g -grecord-command-line -fno-omit-frame-pointer" if user_c_flags else "" 
    update_cxx_flags = f"{user_cxx_flags} -g -grecord-command-line -fno-omit-frame-pointer" if user_cxx_flags else "" 
    update_fc_flags = f"{user_fc_flags} -g -grecord-command-line -fno-omit-frame-pointer" if user_fc_flags else "" 
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, update_c_flags, update_cxx_flags, update_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags)

    # Generate Level 1 oneview report on original app
    oneview_runner.exec(app_builder_env, orig_binary, data_dir, ov_run_dir_orig, run_cmd, maqao_dir, ov_config, 'both', level=1, mpi_run_command="mpirun", mpi_num_processes=1)
    
    #print("Check performance anomalies like I/O time")
    return 0,"",median_value
