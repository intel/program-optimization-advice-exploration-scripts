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

this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
script_name=os.path.basename(os.path.realpath(__file__))

def get_machines():
    log(QaasComponents.BUSINESS_LOGICS, 'Get list of machines to run experiments', mockup=True)
    return ['localhost']

def get_binary_path(ov_config):
    log(QaasComponents.BUSINESS_LOGICS, f'Get binary path from ov file {ov_config}', mockup=True)
    return 'bin/exec'

def run_in_container(src_dir, data_dir, ov_config, ov_run_dir, locus_run_dir, compiler_dir, ov_dir,
                     orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                     user_link_flags, user_target):
    #relative_binary_path = get_binary_path(ov_config)
    ov_run_dir_orig = os.path.join(ov_run_dir, 'orig')
    orig_binary = os.path.join(ov_run_dir_orig, 'exec')
    app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                   user_link_flags, user_target)
    oneview_runner.exec(orig_binary, data_dir, ov_dir, ov_config, ov_run_dir_orig)
    ov_run_dir_opt = os.path.join(ov_run_dir, 'opt')
    opt_binary = os.path.join(ov_run_dir_orig, 'exec')
    app_mutator.exec(src_dir, compiler_dir, opt_binary, locus_run_dir)
    oneview_runner.exec(opt_binary, data_dir, ov_dir, ov_config, ov_run_dir_opt)


def launch(machine, src_dir, data_dir, ov_config, ov_run_dir, locus_run_dir, docker_image, compiler_dir, ov_dir,
           orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
           user_link_flags, user_target):
    log(QaasComponents.BUSINESS_LOGICS, f'MOCKUP: replace with real job submission to machine {machine} using docker image {docker_image}', mockup=True)
    result = subprocess.check_output(f'ssh {machine} python3 {this_script} --src-dir {src_dir} '\
        f'--data_dir {data_dir} --ov_config {ov_config} --ov_run_dir {ov_run_dir} '\
        f'--locus_run_dir {locus_run_dir} --compiler-dir {compiler_dir} --ov_dir {ov_dir} '\
        f'--orig-user-CC {orig_user_CC} --target-CC {target_CC} --user-c-flags \\"{user_c_flags}\\" --user-cxx-flags \\"{user_cxx_flags}\\" --user-fc-flags \\"{user_fc_flags}\\" '\
        f'--user-link-flags \\"{user_link_flags}\\" --user-target {user_target}', 
        shell=True).decode('utf-8')
    print(result)

if __name__ == '__main__':
    parser = ArgumentParser(description='Run a job at the machine in a container.')
    parser.add_argument('--data_dir', nargs='?', required=True) 
    parser.add_argument('--ov_config', nargs='?', required=True)
    parser.add_argument('--ov_run_dir', nargs='?', required=True)
    parser.add_argument('--locus_run_dir', nargs='?', required=True)
    parser.add_argument('--ov_dir', nargs='?', required=True)
    app_builder_builder_argparser(parser, include_binary_path=False)
    args = parser.parse_args()
    log(QaasComponents.BUSINESS_LOGICS, 'Executing job.py script in a container', mockup=True)

    run_in_container(args.src_dir, args.data_dir, args.ov_config, args.ov_run_dir, args.locus_run_dir, args.compiler_dir, args.ov_dir,
                     args.orig_user_CC, args.target_CC, args.user_c_flags, args.user_cxx_flags, args.user_fc_flags,
                     args.user_link_flags, args.user_target)