import argparse
import subprocess
import shutil
import os
from util import load_compiler_env
from fdo_lib import LProfProfiler

def prepare(binary_path, run_dir, data_path):
    os.makedirs(run_dir, exist_ok=True)
    try:
        shutil.copy(binary_path, run_dir)
    except:
        pass
    try:
        shutil.copy(data_path, run_dir)
    except:
        pass
    
def run(binary_path, run_dir, run_cmd, env_var_map, my_env = os.environ.copy()):
    #my_env = os.environ.copy()

    my_env.update(env_var_map)
    #env = load_compiler_env(compiler_dir)
    #my_env.update(env)
    binary_name = os.path.basename(binary_path)
    #true_run_cmd='ls; echo $OMP_NUM_THREADS'
    print(f"run_dir is: {run_dir}")
    # try LProf
    #shutil.copy2(MAQAO_BIN, run_dir) 
    LProfProfiler().run_lprof_loop_profile(run_dir, my_env, run_cmd, binary_name)

# copy executable binary to current directory,
# copy data file to current directory,
# set up env map
# run command replacing <binary> by binary to executable binary
def exec(binary_path, run_dir, data_path, run_cmd, env_var_map, mode):
    if mode == 'prepare' or mode == 'both':
        prepare(binary_path, run_dir, data_path)
    if mode == 'run' or mode == 'both':
        run(binary_path, run_dir, run_cmd, env_var_map)
   
def build_argparser(parser, include_mode=True):
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--run-dir', help='Path to directory to run executable', required=True)
    parser.add_argument('--data-path', help='Path to data file', required=True)
    parser.add_argument('--var', help='Env variable to add', required=False, action='append')
    parser.add_argument('--run-cmd', help='Command to run of the form ... <binary> ... where <binary> represent the executable', required=True)
    if include_mode:
        parser.add_argument('--mode', help='Mode of run', choices=['prepare', 'run', 'both'], required=True)
    #parser.add_argument('--compiler-dir', help='Path to compiler', required=True)

def main():
    parser = argparse.ArgumentParser(description="Run application")
    build_argparser(parser)
    args = parser.parse_args()
    env_var_map = dict([(v.split("=",1)) for v in args.var]) if args.var else {}
    exec(args.binary_path, args.run_dir, args.data_path, args.run_cmd, env_var_map, args.mode)

if __name__ == "__main__": 
    main()