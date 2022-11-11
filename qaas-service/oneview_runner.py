# Contributors: Cedric/Emmanuel
import datetime
import os
from logger import log, QaasComponents
import argparse
import subprocess
from util import generate_timestamp_str
from base_runner import BaseRunner
script_dir=os.path.dirname(os.path.realpath(__file__))

# TODO: refactor with Profiler.py
class OneviewRunner(BaseRunner):
    MAQAO_DIR="/nfs/site/proj/alac/software/UvsqTools/20221102"
    ONEVIEW_OUT_DIR='oneview_out_dir'

    def __init__(self, maqao_dir, level, ov_result_root, ov_config):
        super().__init__(maqao_dir)
        self.level = level
        self.ov_result_root = ov_result_root
        self.ov_config = ov_config
        self.ov_timestamp = int(round(datetime.datetime.now().timestamp()))
        self.run_dir = os.path.join(self.ov_result_root, f'oneview_run_{self.ov_timestamp}')


    @property
    def maqao_bin_dir(self):
        return os.path.join(self.maqao_dir, 'bin')

    @property
    def maqao_lib_dir(self):
        return os.path.join(self.maqao_dir, 'lib')
        
    @property
    def maqao_bin(self):
        return os.path.join(self.maqao_bin_dir, 'maqao')



    # def run(self, binary_path, run_dir, run_cmd, 
    #         mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs, env):
    #     # incorporate OMP and MPI envs
    #     run_env = env.copy()
    #     run_env.update(mpi_envs)
    #     run_env.update(omp_envs)
    #     run_env["OMP_NUM_THREADS"] = str(omp_num_threads)
    #     mpi_command = f"{mpi_run_command} -np {mpi_num_processes}" if mpi_run_command else ""


    #     self.true_run(binary_path, run_dir, run_cmd, run_env, mpi_command)

    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        true_run_cmd = run_cmd.replace('<binary>', binary_path)

        self.ov_result_dir = os.path.join(self.ov_result_root, f'oneview_results_{self.ov_timestamp}')
        os.makedirs(self.ov_result_dir)

        ov_mpi_command = f"--mpi_command=\"{mpi_command}\"" if mpi_command else ""
        ov_run_cmd=f'{self.maqao_bin} oneview -R{self.level} {ov_mpi_command} '\
            f'--run-directory="{run_dir}" '\
            f'xp={self.ov_result_dir} --replace -- {true_run_cmd}'
            #f'--dataset={data_dir} --dataset-handler=copy --run-directory="<dataset>" '\
        print(ov_run_cmd)
        print(self.ov_result_dir)
        subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root)
    
    
def exec(env, binary_path, data_path, ov_result_root, run_cmd, maqao_path, ov_config, mode, 
             mpi_run_command=None, mpi_num_processes=1, omp_num_threads=1, 
             mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=spread"}, omp_envs={}):
    ov_runner = OneviewRunner(maqao_dir=maqao_path, level=1, ov_result_root=ov_result_root, ov_config=ov_config)
    ov_runner.exec (env, binary_path, data_path, run_cmd, mode, mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs)
    log(QaasComponents.OV_RUNNER, f'Result at {ov_runner.ov_result_dir}', mockup=False)
    return ov_runner.ov_result_dir

def main():
    parser = argparse.ArgumentParser(description="Testing loop time aggregation")
    parser.add_argument('--run-path', help='Path to run directory', required=True)
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--src-file', help='Loop source file', required=True)
    parser.add_argument('--loop-line-num', help='Loop head line number', required=True, type=int)
    args = parser.parse_args()
    #time_result, unit_result = aggregate_loop_time(args.run_path, args.binary_path, args.src_file, args.loop_line_num)
    pass

if __name__ == "__main__": 
    main()
