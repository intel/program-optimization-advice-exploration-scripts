import argparse
import subprocess
import shutil
import os
from utils.util import parse_env_map 
from fdo_lib import LProfProfiler
from base_runner import BaseRunner

class AppRunner(BaseRunner):
    def __init__(self, run_dir, maqao_dir):
        super().__init__(maqao_dir)
        self.run_dir = run_dir

    # def exec(self, env, binary_path, data_path, run_cmd, mode,
    #          mpi_run_command, mpi_num_processes, omp_num_threads, 
    #          mpi_envs, omp_envs):
    #     if mode == 'prepare' or mode == 'both':
    #         self.prepare(binary_path, self.run_dir, data_path)
    #     if mode == 'run' or mode == 'both':
    #         self.run(binary_path, self.run_dir, run_cmd, 
    #                  mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs, env)
    

    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        binary_name = os.path.basename(binary_path)
        #true_run_cmd='ls; echo $OMP_NUM_THREADS'

        if not mpi_command:
            #true_run_cmd = self.pin_seq_run_cmd(run_cmd)
            true_run_cmd = run_cmd
            _, last_core = self.get_last_core_and_node()
        else:
            true_run_cmd=f'{mpi_command} {run_cmd}'
            last_core = None

        print(f"run_dir is: {run_dir}")
        # try LProf
        #shutil.copy2(MAQAO_BIN, run_dir) 
        LProfProfiler(self.maqao_dir).run_lprof_loop_profile(run_dir, run_env, true_run_cmd, binary_name, last_core)

# copy executable binary to current directory,
# copy data file to current directory,
# set up env map
# run command replacing <binary> by binary to executable binary
def exec(env, binary_path, maqao_path, run_dir, data_path, run_cmd, mode,
         mpi_run_command=None, mpi_num_processes=1, omp_num_threads=1, 
         mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=spread"}, omp_envs={}):
    app_runner = AppRunner(run_dir, maqao_path)
    app_runner.exec (env, binary_path, data_path, run_cmd, mode, 
                     mpi_run_command, mpi_num_processes, omp_num_threads, 
                     mpi_envs, omp_envs)
   
def build_argparser(parser, include_mode=True):
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--maqao-path', help='Path to maqao root', required=True)
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
    env_var_map = parse_env_map(args)
    my_env = os.environ.copy()
    my_env.update(env_var_map)
    exec(my_env, args.binary_path, args.maqao_path, args.run_dir, args.data_path, args.run_cmd, args.mode)

if __name__ == "__main__": 
    main()