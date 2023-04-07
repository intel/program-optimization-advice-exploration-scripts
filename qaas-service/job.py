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
from qaas_logic_initial_profile import run_initial_profile
from qaas_logic_unicore import run_qaas_UP

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
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags):
    '''QAAS Ruuning Logic/Strategizer Entry Point.''' 

    # Phase 2: Intial profiling and cleaning    
    to_backplane.send(qm.GeneralStatus("QAAS running logic: Initail Profiling and Cleaning"))
    #rc,msg = run_initial_profile(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
    #                 orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
    #                 user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags)
    rc=0
    if rc != 0: 
        to_backplane.send(qm.GeneralStatus(msg))
        return
    to_backplane.send(qm.GeneralStatus("Done Initail Profiling and Cleaning!"))


    # Phase 3.1: Parameter Exploration and Tuning    
    to_backplane.send(qm.GeneralStatus("QAAS running logic: Unicore Parameters Exploration/Tuning"))
    rc,msg = run_qaas_UP(src_dir, data_dir, base_run_dir, ov_config, ov_run_dir, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map, extra_cmake_flags)
    if rc != 0: 
        to_backplane.send(qm.GeneralStatus(msg))
        return
    to_backplane.send(qm.GeneralStatus("Done Unicore Parameters Exploration/Tuning!"))
    return

    to_backplane.send(qm.GeneralStatus("Start Phase 2: INITIAL PROFILING"))
    to_backplane.send(qm.GeneralStatus("Start S2.1"))
    to_backplane.send(qm.GeneralStatus("Done S2.1"))

    to_backplane.send(qm.GeneralStatus("Start S2.2"))
    to_backplane.send(qm.GeneralStatus("Done S2.2"))

    to_backplane.send(qm.GeneralStatus("Start S2.3"))
    to_backplane.send(qm.GeneralStatus("Done S2.3"))

    to_backplane.send(qm.GeneralStatus("Start S2.4"))
    to_backplane.send(qm.GeneralStatus("Done S2.4"))

    to_backplane.send(qm.GeneralStatus("Start S2.5"))
    to_backplane.send(qm.GeneralStatus("Done S2.5"))
    to_backplane.send(qm.GeneralStatus("Done Phase 2: INITIAL PROFILING"))

    to_backplane.send(qm.GeneralStatus("Start Phase 3: PARAMETER EXPLORATION/TUNING"))
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
