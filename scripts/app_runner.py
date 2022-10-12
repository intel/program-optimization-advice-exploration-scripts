import argparse
import subprocess
import shutil
import os

def prepare(binary_path, run_dir, data_path):
    shutil.copy(binary_path, run_dir)
    shutil.copy(data_path, run_dir)
    
def run(binary_path, run_dir, run_cmd, env_var_map):
    my_env = os.environ.copy()
    my_env.update(env_var_map)
    binary_name = os.path.basename(binary_path)
    #true_run_cmd='ls; echo $OMP_NUM_THREADS'
    true_run_cmd = run_cmd.replace('<binary>', './'+binary_name)
    subprocess.run(true_run_cmd, shell=True, env=my_env, cwd=run_dir)
# copy executable binary to current directory,
# copy data file to current directory,
# set up env map
# run command replacing <binary> by binary to executable binary
def exec(binary_path, run_dir, data_path, run_cmd, env_var_map, mode):
    if mode == 'prepare' or mode == 'both':
        prepare(binary_path, run_dir, data_path)
    if mode == 'run' or mode == 'both':
        run(binary_path, run_dir, run_cmd, env_var_map)
   
def build_argparser(parser):
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--run-dir', help='Path to directory to run executable', required=True)
    parser.add_argument('--data-path', help='Path to data file', required=True)
    parser.add_argument('--var', help='Env variable to add', required=False, action='append')
    parser.add_argument('--run-cmd', help='Command to run of the form ... <binary> ... where <binary> represent the executable', required=True)
    parser.add_argument('--mode', help='Mode of run', choices=['prepare', 'run', 'both'], required=True)

def main():
    parser = argparse.ArgumentParser(description="Run application")
    build_argparser(parser)
    args = parser.parse_args()
    env_var_map = dict([(v.split("=",1)) for v in args.var]) 
    exec(args.binary_path, args.run_dir, args.data_path, args.run_cmd, env_var_map, args.mode)

if __name__ == "__main__": 
    main()