import os
import shutil
from abc import ABC, abstractmethod
from utils.runcmd import QAASRunCMD

class BaseRunner(ABC):
    def __init__(self, maqao_dir):
        self._maqao_dir = maqao_dir
    
    @property
    def maqao_dir(self):
        return self._maqao_dir

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

    def pin_seq_run_cmd(self, run_cmd):
        last_node, last_core = self.get_last_core_and_node()
        pinning_cmd = f'/usr/bin/numactl -m {last_node} -C {last_core}'

        seq_run_cmd = f'{pinning_cmd} {run_cmd}'
        return seq_run_cmd

    def get_last_core_and_node(self):
        rc, cmdout = QAASRunCMD(0).run_local_cmd("/usr/bin/numactl -H | awk '/cpus/ && $2>=max {max=$2}; END{print max}'")
        last_node = int(cmdout.decode("utf-8"))
        rc, cmdout = QAASRunCMD(0).run_local_cmd(f"/usr/bin/numactl -H | grep 'node {last_node}' | grep  'cpus' |cut -d: -f2|xargs -n1|sort -r -n|head -1")
        last_core = int(cmdout.decode("utf-8"))
        return last_node,last_core