# Contributors: Cedric/Emmanuel
import datetime
import os
from logger import log, QaasComponents
import argparse
import subprocess
from utils.util import generate_timestamp_str
from base_runner import BaseRunner
script_dir=os.path.dirname(os.path.realpath(__file__))

# TODO: refactor with Profiler.py
class OneviewRunner(BaseRunner):
    #MAQAO_DIR="/nfs/site/proj/alac/software/UvsqTools/20221102"
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

    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        true_run_cmd = run_cmd.replace('<binary>', binary_path)
        pinning_cmd = "" if mpi_command else f"--pinning-command=\"{self.get_pinning_cmd()}\""

        self.ov_result_dir = os.path.join(self.ov_result_root, f'oneview_results_{self.ov_timestamp}')
        os.makedirs(self.ov_result_dir)

        ov_mpi_command = f"--mpi-command=\"{mpi_command}\"" if mpi_command else ""
        ov_filter_option = '--filter="{type=\\\"number\\\", value=4}"' if self.level != 1 else ''
        ov_run_cmd=f'{self.maqao_bin} oneview -R{self.level} {ov_mpi_command} '\
            f'--run-directory="{run_dir}" {pinning_cmd} '\
            f'--replace xp={self.ov_result_dir} '\
            f'{ov_filter_option} '\
            f'-- {true_run_cmd}'
            #f'--dataset={data_dir} --dataset-handler=copy --run-directory="<dataset>" '\
        print(ov_run_cmd)
        print(self.ov_result_dir)
        run_env["LD_LIBRARY_PATH"] = run_env.get("LD_LIBRARY_PATH") + ":" + self.maqao_lib_dir
        result = subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True

        print(f"OneView Level {self.level} failed! Fallback to lower level")
        new_level = self.level - 1
        if new_level == 0:
            return False
        ov_run_cmd = ov_run_cmd.replace(f"-R{self.level}", "-R{new_level}")
        self.level = new_level
        print(ov_run_cmd)
        result = subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True

        print(f"OneView Level {self.level} failed! Fallback to lower level")
        new_level = self.level - 1
        if new_level == 0:
            return False
        ov_run_cmd = ov_run_cmd.replace(f"-R{self.level}", "-R{new_level}")
        self.level = new_level
        print(ov_run_cmd)
        result = subprocess.run(ov_run_cmd, shell=True, env=run_env, cwd=self.ov_result_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        else:
            return False

def exec(env, binary_path, data_path, ov_result_root, run_cmd, maqao_path, ov_config, mode, 
             level=1, mpi_run_command=None, mpi_num_processes=1, omp_num_threads=1, 
             mpi_envs={"I_MPI_PIN_PROCESSOR_LIST":"all:map=spread"}, omp_envs={}):
    ov_runner = OneviewRunner(maqao_dir=maqao_path, level=level, ov_result_root=ov_result_root, ov_config=ov_config)
    success = ov_runner.exec (env, binary_path, data_path, run_cmd, mode, mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs)
    if success:
        log(QaasComponents.OV_RUNNER, f'Result at {ov_runner.ov_result_dir}', mockup=False)
        return ov_runner.ov_result_dir
    else:
        return None

def main():
    parser = argparse.ArgumentParser(description="Testing loop time aggregation")
    parser.add_argument('--run-path', help='Path to run directory', required=True)
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--src-file', help='Loop source file', required=True)
    parser.add_argument('--loop-line-num', help='Loop head line number', required=True, type=int)
    args = parser.parse_args()
    pass

if __name__ == "__main__": 
    main()