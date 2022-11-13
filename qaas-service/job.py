# Contributors: Hafid/David
from argparse import ArgumentParser
import subprocess
import os

import app_runner
import app_builder
import app_mutator
import oneview_runner
from logger import log, QaasComponents
from app_builder import build_argparser as app_builder_builder_argparser
from util import parse_env_map 
from utils import qaas_message as qm
import socket

this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
script_name=os.path.basename(os.path.realpath(__file__))

class ServiceMessageSender:
    def __init__(self, comm_port):
        self.comm_port = comm_port
        self.connect()

    def send(self, data):
        if self.msg_sender:
            self.msg_sender.sendall(data.encode())
        self.close()
        self.connect()
        
    def connect(self):
        self.msg_sender = socket.create_connection(("localhost", self.comm_port)) if self.comm_port else None
        
    def close(self):
        if self.msg_sender:
            self.msg_sender.close()
        
        
def get_machines():
    log(QaasComponents.BUSINESS_LOGICS, 'Get list of machines to run experiments', mockup=True)
    return ['localhost']

def get_binary_path(ov_config):
    log(QaasComponents.BUSINESS_LOGICS, f'Get binary path from ov file {ov_config}', mockup=True)
    return 'bin/exec'

def run_in_container(to_backplane, src_dir, data_dir, ov_config, ov_run_dir, locus_run_root, compiler_dir, maqao_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target, user_target_location, run_cmd, env_var_map):
    #relative_binary_path = get_binary_path(ov_config)
    ov_run_dir_orig = os.path.join(ov_run_dir, 'orig')
    orig_binary = os.path.join(ov_run_dir_orig, 'exec')
    to_backplane.send(qm.GeneralStatus("Start Building orig app"))
    app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both')
    to_backplane.send(qm.GeneralStatus("Done Building orig app"))
    to_backplane.send(qm.GeneralStatus("Start Running orig app"))
    oneview_runner.exec(app_builder_env, orig_binary, data_dir, ov_run_dir_orig, run_cmd, maqao_dir, ov_config, 'both', None)
    to_backplane.send(qm.GeneralStatus("Done Running orig app"))
    ov_run_dir_opt = os.path.join(ov_run_dir, 'opt')
    opt_binary = os.path.join(ov_run_dir_opt, 'exec')
    to_backplane.send(qm.GeneralStatus("Start Tuning orig app"))
    mutator_env = app_mutator.exec(locus_run_root, src_dir, compiler_dir, maqao_dir, opt_binary, orig_user_CC, target_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
         data_dir, run_cmd, env_var_map, user_target_location) 
    #                 locus_run_dir)
    to_backplane.send(qm.GeneralStatus("Done Tuning orig app"))
    to_backplane.send(qm.GeneralStatus("Start Running tuned app"))
    oneview_runner.exec(mutator_env, opt_binary, data_dir, ov_run_dir_opt, run_cmd, maqao_dir, ov_config, 'both', None)
    to_backplane.send(qm.GeneralStatus("Done Running tuned app"))


def launch(machine, src_dir, data_dir, ov_config, ov_run_dir, locus_run_dir, docker_image, compiler_dir, ov_dir,
           orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
           user_link_flags, user_target, user_target_location, env_var_map, run_cmd):
    log(QaasComponents.BUSINESS_LOGICS, f'MOCKUP: replace with real job submission to machine {machine} using docker image {docker_image}', mockup=True)
    #result = subprocess.check_output(f'ssh {machine} python3 {this_script} --src-dir {src_dir} '\
    launch_cmd = f'python3 {this_script} --src-dir {src_dir} '\
        f'--data_dir {data_dir} --ov_config {ov_config} --ov_run_dir {ov_run_dir} '\
        f'--locus_run_dir {locus_run_dir} --compiler-dir {compiler_dir} --ov_dir {ov_dir} '\
        f'--orig-user-CC {orig_user_CC} --target-CC {target_CC} --user-c-flags "{user_c_flags}" --user-cxx-flags "{user_cxx_flags}" --user-fc-flags "{user_fc_flags}" '\
        f'--user-link-flags "{user_link_flags}" --user-target {user_target} --user-target-location {user_target_location} '\
        f'--run-cmd "{run_cmd}"'
    launch_cmd += "".join([f' --var {k}={v}' for k,v in env_var_map.items()])
    log(QaasComponents.BUSINESS_LOGICS, f'MOCKUP: {launch_cmd}', mockup=True)
    result = subprocess.check_output(launch_cmd, shell=True).decode('utf-8')
    print(result)

if __name__ == '__main__':
    parser = ArgumentParser(description='Run a job at the machine in a container.')
    parser.add_argument('--data_dir', nargs='?', required=True) 
    parser.add_argument('--ov_config', nargs='?', required=True)
    parser.add_argument('--ov_run_dir', nargs='?', required=True)
    parser.add_argument('--locus_run_dir', nargs='?', required=True)
    parser.add_argument('--ov_dir', nargs='?', required=True)
    parser.add_argument('--run-cmd', help='Command to run of the form ... <binary> ... where <binary> represent the executable', required=True)
    parser.add_argument('--var', help='Env variable to add', required=False, action='append')
    parser.add_argument('--comm-port', nargs='?', type=int, default=None) 
    app_builder_builder_argparser(parser, include_binary_path=False, include_mode=False)
    args = parser.parse_args()
    log(QaasComponents.BUSINESS_LOGICS, 'Executing job.py script in a container', mockup=True)

    env_var_map = parse_env_map(args)
    #import time
    #import sys
    import socket
    
    to_backplane = ServiceMessageSender(args.comm_port)
    to_backplane.send(qm.BeginJob())
    #connect = SshConnector(5001)
    #connect.connect()
    #print(f"connected")
    #time.sleep(2)
    #sys.exit(0)
    run_in_container(to_backplane, args.src_dir, args.data_dir, args.ov_config, args.ov_run_dir, args.locus_run_dir, args.compiler_dir, args.ov_dir,
                     args.orig_user_CC, args.target_CC, args.user_c_flags, args.user_cxx_flags, args.user_fc_flags,
                     args.user_link_flags, args.user_target, args.user_target_location, args.run_cmd, env_var_map)
    to_backplane.send(qm.EndJob())
    to_backplane.close()
