#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# MIT License

# Copyright (c) 2023 Intel-Sandbox
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
###############################################################################
# HISTORY
# Created June 2022
# Updated October 2022
# Contributors: Hafid/David

import os
import logging
from utils.runcmd import QAASRunCMD
import tempfile

# define constants

class QAASJobException(Exception):
    def __init__(self, rc):
        self.rc = rc

class QAASJobSubmit:
    """."""
    def __init__(self, system_compilers, user_compiler, user_application, user_runtime, provisioner,
                 no_compiler_default, no_compiler_flags,
                 parallel_compiler_runs, enable_parallel_scale):
        self.compilers = system_compilers
        self.compiler = user_compiler
        self.application = user_application
        self.runtime = user_runtime
        self.provisioner = provisioner
        self.no_compiler_default = no_compiler_default
        self.no_compiler_flags = no_compiler_flags
        self.parallel_compiler_runs = parallel_compiler_runs
        self.enable_parallel_scale = enable_parallel_scale

    def run_container(self, app_cmd, mount_map, user_ns_root, network_host=False, cap_add=False, debug=False):
        mount_flags = "".join([f' -v {k}:{v}' for k,v in mount_map.items()])
        start_container_flags, run_cmd = self.build_podman_run_command(app_cmd, network_host, cap_add, mount_flags, user_ns_root)
        print(f'Container cmd: {run_cmd}')
        try:
            if debug:
                # Split the container command in multiple steps enabling state capturing
                self.run_remote_job_cmd(f"'podman create -it {start_container_flags}'")

                self.create_container_info_tarball(app_cmd, mount_map, network_host, cap_add, run_cmd)
                # now we can use the created container to run command
                self.run_remote_job_cmd(f"'podman start {self.provisioner.app_name}'")
                self.run_remote_job_cmd(f"'podman exec {self.provisioner.app_name} {app_cmd}'")
                job_cmd = f"'podman stop {self.provisioner.app_name}'"
            else:
                job_cmd = f"'{run_cmd}'"

            # running the last command or the only cocommand in non-debug mode
            rc, _ = self.run_remote_job_cmd(job_cmd)
            return rc
        except QAASJobException as exp:
            # try to stop and remove the container on errors
            try:
                self.run_remote_job_cmd(f"'podman stop {self.provisioner.app_name}'")
            except:
                pass
            # return original error
            return exp.rc

    def run_native(self, run_cmd):
        job_cmd = f"{run_cmd}"
        try:
            rc, _ = self.run_remote_job_cmd(job_cmd)
            return rc
        except QAASJobException as exp:
            # return original error
            return exp.rc

    def create_container_info_tarball(self, app_cmd, mount_map, network_host, cap_add, run_cmd):
        _, tmp_dir=self.run_remote_job_cmd("mktemp -d -t qaas-XXXXXXXX")
        tmp_dir = tmp_dir.strip()
        self.run_remote_job_cmd(f"'echo {run_cmd} > {tmp_dir}/runcmd_orig.sh'")
        tarball_mount_flags = "".join([f' -v \$\(pwd\)/{k}:{v}' for k,v in mount_map.items()])
        _, tarball_run_cmd = self.build_podman_run_command(app_cmd, network_host, cap_add, tarball_mount_flags, user_ns_root)
        self.run_remote_job_cmd(f"'echo {tarball_run_cmd} > {tmp_dir}/runcmd_tarball.sh'")
        for host_dir, container_dir in mount_map.items():
            _, mount_type=self.run_remote_job_cmd(f"stat -f -c %T {host_dir}")
            mount_type = mount_type.strip()
            if mount_type == "nfs" or mount_type == "autofs":
                        # Skipping mounted drives
                continue
            out_host_dir = f"{tmp_dir}/{host_dir}"
            self.run_remote_job_cmd(f"mkdir -p {out_host_dir}")
            print(f"Copying out {host_dir} from container {container_dir}")
            self.run_remote_job_cmd(f"podman cp {self.provisioner.app_name}:{container_dir} {out_host_dir}")
        remote_tarball = f"{tmp_dir}.tar.gz"
        self.run_remote_job_cmd(f"'cd {tmp_dir}/.. && tar cfz {remote_tarball} {os.path.basename(tmp_dir)}'")
        download_dir = tempfile.mkdtemp()
        self.copy_remote_file(remote_tarball, download_dir)
        print(f"Container tarball in: {os.path.join(download_dir, os.path.basename(remote_tarball))}")

    def build_podman_run_command(self, app_cmd, network_host, cap_add, mount_flags, user_ns_root):
        network_host_flag = " --network=host " if network_host else ""
        cap_add_flag = " --cap-add  SYS_ADMIN,SYS_PTRACE" if cap_add else ""
        user_ns_root_flag = " --user=root " if user_ns_root else ""
        start_container_flags = "--rm --name " + self.provisioner.app_name + \
                     user_ns_root_flag + \
                     network_host_flag + mount_flags + \
                     cap_add_flag + \
                     " " + self.provisioner.image_name
        run_cmd = "podman run "+ start_container_flags + " " + app_cmd
        return start_container_flags,run_cmd

    def copy_remote_file(self, remote_file, local_dir):
        rc = 0
        rc, cmdout = QAASRunCMD(self.provisioner.comm_port, self.provisioner.machine, self.provisioner.ssh_port, self.provisioner.user).copy_remote_file(remote_file, local_dir)
        if rc == 0:
            logging.debug(cmdout)
            return 0, cmdout
        else:
            raise QAASJobException(rc)

    def run_remote_job_cmd(self, job_cmd):
        rc = 0
        cmd_runner = QAASRunCMD(self.provisioner.comm_port, self.provisioner.machine, self.provisioner.ssh_port, self.provisioner.user)
        if self.provisioner.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(job_cmd)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(job_cmd)
        if rc == 0:
            logging.debug(cmdout)
            return 0, cmdout
        else:
            raise QAASJobException(rc)

    def run_job(self, container=True, user_ns_root=False):
        """Run job script itself"""
        container_script_root = self.provisioner.get_script_root(container)
        compiler_root = self.provisioner.get_compiler_root()
        intel_compiler_root = self.provisioner.get_intel_compiler_root()
        gnu_compiler_root = self.provisioner.get_gnu_compiler_root()
        compiler_subdir = self.provisioner.get_compiler_subdir(self.compiler["USER_CC"], self.compiler["USER_CC_VERSION"])
        ov_run_dir = self.provisioner.get_workdir("oneview_runs")
        locus_run_dir = self.provisioner.get_workdir("locus_runs")
        base_run_dir = self.provisioner.get_workdir("base_runs")
        dataset_dir = os.path.join(self.provisioner.get_workdir("dataset"), self.provisioner.app_name)
        qaas_reports_dir = self.provisioner.get_workdir("qaas_reports")
        ov_dir = self.provisioner.analyzers["QAAS_ONEVIEW_DIRECTORY"]
        container_ov_dir_path = "/opt/maqao" if container else ov_dir
        container_app_builder_path = "/app/builder" if container else self.provisioner.get_workdir("build")
        container_app_dataset_path = "/app/dataset" if container else dataset_dir
        container_app_oneview_path = "/app/oneview_runs" if container else ov_run_dir
        container_app_locus_path = "/app/locus_runs" if container else locus_run_dir
        container_app_base_path = "/app/base_runs" if container else base_run_dir
        container_app_reports_path = "/app/qaas_reports" if container else qaas_reports_dir
        # The current load script seems to require the same path
        container_compiler_root=compiler_root
        app_run_info = self.application["RUN"]
        env_var_map=app_run_info["APP_ENV_MAP"]
        env_var_flags = "".join([f' --var {k}={v}' for k,v in env_var_map.items()])
        # Pass initial profiling parameters as environment variables
        env_var_flags += f' --var QAAS_DEFAULT_REPETITIONS={self.provisioner.initial_profile_params["QAAS_DEFAULT_REPETITIONS"]}'
        env_var_flags += f' --var QAAS_MAX_ALLOWED_EXEC_TIME={self.provisioner.initial_profile_params["QAAS_MAX_ALLOWED_EXEC_TIME"]}'
        # Pass FOM regex as environment variable if any
        if app_run_info.get("FOM_REGEX"):
            env_var_flags += f' --var FOM_REGEX={app_run_info["FOM_REGEX"]}'
            fom_type = app_run_info["FOM_TYPE"] if app_run_info.get("FOM_TYPE") else "RATE"
            env_var_flags += f' --var FOM_TYPE={fom_type}'
            fom_unit = app_run_info["FOM_UNIT"] if app_run_info.get("FOM_UNIT") else "NA"
            env_var_flags += f' --var FOM_UNIT="{fom_unit}"'
        # Enable search when LTO flags are available
        env_var_flags += f' --var QAAS_ENABLE_LTO=1' if "QAAS_ENABLE_LTO" in os.environ else ""
        # Check if we need USER_EXTRA_CMAKE_FLAGS
        user_extra_cmake_flags = self.compiler["USER_EXTRA_CMAKE_FLAGS"] if "USER_EXTRA_CMAKE_FLAGS" in self.compiler.keys() else ""
        # Check if need to disable automatic search for best default compiler and/or compiler flags
        disable_best_compiler_default = "--no-compiler-default" if self.no_compiler_default else ""
        disable_best_compiler_flags = "--no-compiler-flags" if self.no_compiler_flags else ""
        enable_parallel_scale_option = "-s" if self.enable_parallel_scale != 0 else ""
        if self.enable_parallel_scale == 'best-compiler':
            enable_parallel_scale_option += " --enable-scale-on-best-compiler"
        # Setup per-compiler location to isolate environment
        multi_compilers_dirs = ";".join([f"{compiler}:{os.path.join(container_compiler_root, self.provisioner.get_compiler_subdir(compiler, 'latest'))}" for compiler in self.provisioner.get_enabled_compilers()])
        # Below used --network=host so script can communicate back to launcher via ssh forwarding.  Can try to restrict to self.provisioner.comm_port if needed
        app_cmd = f"/usr/bin/env python3 {container_script_root}/qaas-service/job.py "+ \
                    f' --src-dir {os.path.join(container_app_builder_path, self.provisioner.app_name)}'+ \
                    f' --data_dir {os.path.join(container_app_dataset_path, self.provisioner.git_data_download_path)} --ov_config unused --ov_run_dir {container_app_oneview_path}'+ \
                    f' --base_run_dir {container_app_base_path} --locus_run_dir {container_app_locus_path}' + \
                    f' --compiler-dir {os.path.join(container_compiler_root, compiler_subdir)} --ov_dir {container_ov_dir_path}'+ \
                    f' --orig-user-CC {self.compiler["USER_CC"]} --target-CC {self.compiler["USER_CC"]} --user-c-flags="{self.compiler["USER_C_FLAGS"]}"'+ \
                    f' --user-cxx-flags="{self.compiler["USER_CXX_FLAGS"]}" --user-fc-flags="{self.compiler["USER_FC_FLAGS"]}"'+ \
                    f' --user-link-flags="{self.compiler["USER_LINK_FLAGS"]}"'+ \
                    f' --extra-cmake-flags="{user_extra_cmake_flags}"' + \
                    f' --user-target {self.compiler["USER_TARGET"]} --user-target-location {self.compiler["USER_TARGET_LOCATION"]}'+ \
                    f'{env_var_flags}'+ \
                    f' --run-cmd "{app_run_info["APP_RUN_CMD"]}"' + \
                    f' {disable_best_compiler_default}' + \
                    f' {disable_best_compiler_flags}' + \
                    f' --parallel-compiler-runs {self.parallel_compiler_runs}' + \
                    f' {enable_parallel_scale_option}' + \
                    f' --mpi-scale-type {self.runtime["MPI"]}' + \
                    f' --openmp-scale-type {self.runtime["OPENMP"]}' + \
                    f' --multi-compilers_dirs "{multi_compilers_dirs}"' + \
                    f" --comm-port {self.provisioner.comm_port}"
        if container:
            mount_map = { ov_dir:container_ov_dir_path, script_root:container_script_root,
                     self.provisioner.get_workdir("build") :container_app_builder_path,
                     ov_run_dir:container_app_oneview_path,
                     base_run_dir:container_app_base_path,
                     locus_run_dir:container_app_locus_path,
                     qaas_reports_dir:container_app_reports_path,
                     compiler_root:container_compiler_root,
                     dataset_dir:container_app_dataset_path}

            if intel_compiler_root:
                mount_map[intel_compiler_root] = intel_compiler_root

            if gnu_compiler_root:
                mount_map[gnu_compiler_root] = gnu_compiler_root

            job_run = self.run_container(app_cmd, mount_map, user_ns_root, network_host=True, cap_add=True, debug=False)
        else:
            job_run = self.run_native(app_cmd)

        return job_run
