# Contributors: Hafid/David
from argparse import ArgumentParser
import subprocess
import os
import sys

import app_builder
import app_runner
import lprof_runner
import oneview_runner
from logger import log, QaasComponents
#from app_builder import build_argparser as app_builder_builder_argparser
#from utils.util import parse_env_map
from qaas_logic_compile import compile_binaries as compile_all

#this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
#script_name=os.path.basename(os.path.realpath(__file__))
#LPROF_WALLTIME_LUA_FILE=os.path.join(script_dir, 'lua_scripts', 'lprof_walltime.lua')

DEFAULT_REPETITIONS = 1

def run_qaas_UP(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags):

    '''Execute QAAS Running Logic: UNICORE PARAMETER EXPLORATION/TUNING'''

    # First build all options
    compiled_options = compile_all(src_dir, base_run_dir, compiler_dir, 
                orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                user_link_flags, user_target, user_target_location, extra_cmake_flags)
    
    # Compare options
    rc=0
    msg="success"
#    return rc,msg
    for binary_path,app_env in compiled_options:
        # Setup run directory and launch initial run
        print("#######################################################")
        print(f"binary_name={binary_path}")
        print(f"app_env={app_env}")
        basic_run = app_runner.exec(app_env, binary_path, data_dir, base_run_dir_orig, run_cmd, 'both', DEFAULT_REPETITIONS, "mpirun")
        tmp = [str(x) for x in basic_run.exec_times]

        # Check execution in defined range
        median_value = basic_run.compute_median_exec_time()
        print("#######################################################")
    
    return rc,msg
