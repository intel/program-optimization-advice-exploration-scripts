from argparse import ArgumentParser
import subprocess
import os

import app_runner
import app_builder
import app_mutator
import oneview_runner

this_script=os.path.realpath(__file__)
script_dir=os.path.dirname(os.path.realpath(__file__))
script_name=os.path.basename(os.path.realpath(__file__))

def get_machines():
    print('MOCKUP: get list of machines to run experiments')
    return ['localhost']

def get_binary_path(ov_config):
    print(f'MOCKUP:  get binary path from ov file {ov_config}')
    return 'bin/exec'

def run_in_container(src_dir, data_dir, ov_config, ov_run_dir):
    relative_binary_path = get_binary_path(ov_config)
    orig_binary = app_builder.exec(src_dir, relative_binary_path)
    oneview_runner.exec(orig_binary, data_dir, ov_config, os.path.join(ov_run_dir, 'orig'))
    opt_binary = app_mutator.exec(src_dir, relative_binary_path)
    oneview_runner.exec(opt_binary, data_dir, ov_config, os.path.join(ov_run_dir, 'opt'))


def launch(machine, src_dir, data_dir, ov_config, ov_run_dir, docker_image):
    print(f'MOCK: replace with real job submission to machine {machine} using docker image {docker_image}')
    result = subprocess.check_output(f'ssh {machine} python3 {this_script} \
        --src_dir {src_dir} --data_dir {data_dir} --ov_config {ov_config} --ov_run_dir {ov_run_dir}', shell=True).decode('utf-8')
    print(result)

if __name__ == '__main__':
    parser = ArgumentParser(description='Run a job at the machine in a container.')
    parser.add_argument('--src_dir', nargs='?', required=True) 
    parser.add_argument('--data_dir', nargs='?', required=True) 
    parser.add_argument('--ov_config', nargs='?', required=True)
    parser.add_argument('--ov_run_dir', nargs='?', required=True)
    args = parser.parse_args()
    print('MOCKUP: this is executed in a container')

    run_in_container(args.src_dir, args.data_dir, args.ov_config, args.ov_run_dir)