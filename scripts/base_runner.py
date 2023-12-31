import os
import shutil
from abc import ABC, abstractmethod

class BaseRunner(ABC):
    def __init__(self):
        pass

    def prepare(self, binary_path, data_path):
        os.makedirs(self.run_dir, exist_ok=True)
        try:
            shutil.copy(binary_path, self.run_dir)
        except:
            pass
        try:
            if os.path.isfile(data_path):
                shutil.copy(data_path, self.run_dir)
            else:
                assert os.path.isdir(data_path)
                for file in os.listdir(data_path):
                    shutil.copy(os.path.join(data_path, file), self.run_dir)
        except:
            pass

    def run(self, binary_path, run_cmd,
            mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs, env):
        run_env = env.copy()
        run_env.update(mpi_envs)
        run_env.update(omp_envs)
        run_env["OMP_NUM_THREADS"] = str(omp_num_threads)
        mpi_command = f"{mpi_run_command} -np {mpi_num_processes}" if mpi_run_command else ""

        #my_env.update(env_var_map)
        #env = load_compiler_env(compiler_dir)
        #my_env.update(env)
        self.true_run(binary_path, self.run_dir, run_cmd, run_env, mpi_command)

    # Subclass override to do the real run
    @abstractmethod
    def true_run(self, binary_path, run_dir, run_cmd, run_env, mpi_command):
        pass

    def exec(self, env, binary_path, data_path, run_cmd, mode,
             mpi_run_command, mpi_num_processes, omp_num_threads,
             mpi_envs, omp_envs):
        if mode == 'prepare' or mode == 'both':
            self.prepare(binary_path, data_path)
            print(self.run_dir)

        if mode == 'run' or mode == 'both':
            self.run(binary_path, run_cmd,
                     mpi_run_command, mpi_num_processes, omp_num_threads, mpi_envs, omp_envs, env)
