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
import tarfile
import pandas as pd
import shutil
import logging
import urllib.parse
import sys
from utils.runcmd import QAASRunCMD
from utils.comm import ServiceMessageReceiver
from utils.util import split_compiler_combo, generate_timestamp, timestamp_str

# define QAAS GIT-related constants
GIT_USER = "USER"
GIT_TOKEN = "TOKEN"
GIT_BRANCH = "BRANCH"
GIT_SRC_URL = "SRC_URL"
#GIT_GET_EXTRA_MODULES = "GET_EXTRA_MODULES"

GIT_DATA_USER = "DATA_USER"
GIT_DATA_TOKEN = "DATA_TOKEN"
GIT_DATA_BRANCH = "DATA_BRANCH"
GIT_DATA_URL = "DATA_URL"
GIT_DATA_BRANCH = "DATA_BRANCH"
GIT_DATA_DOWNLOAD_PATH = "DATA_DOWNLOAD_PATH"
GIT_DATA_COPY_FROM_FS  = "DATA_COPY_FROM_FS"
DATASET_LABEL  = "DATASET_LABEL"

# define directory structure constants
WORKDIR_ROOT_INDEX  = 0
BUILDDIR_INDEX      = 1
RUNDIR_INDEX        = 2
BASEDIR_INDEX       = 3
OVDIR_INDEX         = 4
LOCUSDIR_INDEX      = 5
DATADIR_INDEX       = 6
QAAS_REPORTS_INDEX  = 7
QAAS_RUN_TYPES = ["base_runs", "oneview_runs", "locus_runs"]


class QAASEnvProvisioner:
    """Object to manage environment setup."""
    def __init__(self, service_dir, script_root,
                 account, app_name, git_params,
                 access_params, container,
                 compilers, compiler_mappings,
                 initial_profile_params,
                 analyzers, comm_port,
                 remote_job,
                 service_msg_recv_handler,
                 launch_output_dir):
        logging.debug("QAASEnvProvisioner Constructor")
        # save mete information
        self._session_id = generate_timestamp()
        self._service_dir = service_dir
        self.script_root = script_root
        self.account = account
        self.app_name = app_name
        # setup working directories
        # NOTE: Following append order related to the INDEX values and also there are
        # len(QAAS_RUN_TYPES) run directories allocated assumed
        # (BASEDIR_INDEX, OVDIR_INDEX, LOCUSDIR_INDEX) matches QAAS_RUN_TYPES array order
        # qaas_reports holds generated csv reports
        self.work_dirs = []
        self.work_dirs.append(os.path.join(self.service_dir, self.account, self.app_name))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "build"))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "run"))
        for workdir in QAAS_RUN_TYPES:
            self.work_dirs.append(os.path.join(self.work_dirs[RUNDIR_INDEX], workdir))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "dataset"))
        self.work_dirs.append(os.path.join(self.work_dirs[RUNDIR_INDEX], 'qaas_reports'))
        # save git configuration
        self.git_user = git_params[GIT_USER]
        self.git_token = git_params[GIT_TOKEN]
        self.git_branch = git_params[GIT_BRANCH]
        self.git_src_url = git_params[GIT_SRC_URL]

        self.git_data_user = git_params[GIT_DATA_USER]
        self.git_data_token = git_params[GIT_DATA_TOKEN]
        self.git_data_branch = git_params[GIT_DATA_BRANCH]
        self.git_data_url = git_params[GIT_DATA_URL]
        self.git_data_download_path = git_params[GIT_DATA_DOWNLOAD_PATH]
        self.git_data_copy_from_fs = git_params[GIT_DATA_COPY_FROM_FS] if GIT_DATA_COPY_FROM_FS in git_params.keys() else ""
        self.dataset_label = git_params[DATASET_LABEL] if DATASET_LABEL in git_params.keys() else ""
        # save target machine access parameters
        self.user = access_params["QAAS_USER"]
        self.ssh_port = access_params["QAAS_SSH_PORT"]
        self.machine = access_params["QAAS_MACHINES_POOL"]
        self.image_name = container["QAAS_CONTAINER_IMAGE"] + ":" + container["QAAS_CONTAINER_TAG"]
        self.image_uid = container["QAAS_CONTAINER_UID"]
        self.remote_job = remote_job
        self.comm_port = int(comm_port) if self.remote_job else 0
        self.msg_server = ServiceMessageReceiver(("localhost", self.comm_port), service_msg_recv_handler=service_msg_recv_handler) if remote_job else None
        self.compiler_root = compilers["QAAS_COMPILERS_ROOT_DIRECTORY"]
        self.intel_compiler_root = compilers["QAAS_INTEL_COMPILERS_DIRECTORY"] if compilers["QAAS_INTEL_COMPILERS_DIRECTORY"] else ""
        self.gnu_compiler_root = compilers["QAAS_GNU_COMPILERS_DIRECTORY"] if compilers["QAAS_GNU_COMPILERS_DIRECTORY"] else ""
        self.enabled_compilers = compilers["QAAS_ENABLED_COMPILERS"].replace(' ', '').split(',')
        self.compiler_mappings = compiler_mappings
        self._launch_output_dir = launch_output_dir
        self.analyzers = analyzers
        self.initial_profile_params = initial_profile_params

    def get_script_root(self, container):
        script_root = self.script_root
        container_script_root = "/app/QAAS_SCRIPT_ROOT"  if container else script_root
        return container_script_root

    @property
    def service_dir(self):
        return self.sessioned_dir(self._service_dir)

    @property
    def launch_output_dir(self):
        return self.sessioned_dir(self._launch_output_dir)

    def sessioned_dir(self, root):
        return os.path.join(root, timestamp_str(self.session_id))

    # Getting session id useful to identify different runs
    @property
    def session_id(self):
        return self._session_id

    def get_compiler_subdir(self, compiler_combo, version):
        # Need to handle mpiicc-icc
        _, compiler = split_compiler_combo(compiler_combo)
        return self.compiler_mappings[f"{compiler}_{version}"]

    def get_compiler_root(self):
        return self.compiler_root

    def get_intel_compiler_root(self):
        return self.intel_compiler_root

    def get_gnu_compiler_root(self):
        return self.gnu_compiler_root

    def get_enabled_compilers(self):
        return self.enabled_compilers

    def get_compilerdir(self):
        return "/nfs/site/proj/openmp/compilers/intel/2022"

    def get_workdir(self, target):
        """Get a given dir."""
        if target == "root":
            return self.work_dirs[WORKDIR_ROOT_INDEX]
        elif target == "build":
            return self.work_dirs[BUILDDIR_INDEX]
        elif target == "run":
            return self.work_dirs[RUNDIR_INDEX]
        elif target == "base_runs":
            return self.work_dirs[BASEDIR_INDEX]
        elif target == "oneview_runs":
            return self.work_dirs[OVDIR_INDEX]
        elif target == "locus_runs":
            return self.work_dirs[LOCUSDIR_INDEX]
        elif target == "dataset":
            return self.work_dirs[DATADIR_INDEX]
        elif target == "qaas_reports":
            return self.work_dirs[QAAS_REPORTS_INDEX]

    def create_work_dirs(self, container=True, user_ns_root=False):
        """Create working directories."""
        logging.info("Create Working Directories on %s", self.machine)
        # craete dirs
        cmds = "mkdir -p " + self.work_dirs[0]
        for index in range(1, len(self.work_dirs), 1):
            cmds = cmds + " && " + "mkdir -p " + self.work_dirs[index]
        #cmds = "'" + cmds + "'"
        cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)
        if self.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(cmds)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(cmds)
        if rc != 0:
            return rc
        # update ownership rights for container runs
        if container and not user_ns_root:
            rc = self.update_workdir_owner()
        return rc

    def update_workdir_owner(self):
        """Update working directories ownership rights to build & run in a container."""
        cmdline = "podman unshare chown -R :" + self.image_uid + " " + self.get_workdir("root")
        cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)
        if self.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(cmdline)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(cmdline)
        return rc

    def clone_source_repo(self):
        """Clone the application's GIT repo."""
        logging.info("Cloning application GIT repo on %s", self.machine)
        target_branch, git_url = self.generate_git_url_branch(self.git_branch, self.git_src_url,
                                                              self.git_user, self.git_token)
        cmdline = "cd " + self.get_workdir("build") + \
                  " && if [[ ! -d " + self.app_name + " ]]; then" + \
                  " git clone -b " + target_branch + \
                  " " + git_url + " " + self.app_name + \
                  " && cd " + self.app_name + \
                  f" && if [[ -f .gitmodules ]]; then git submodule update --init --recursive; fi" + \
                  " && cd .." + \
                  " && rm -rf " + self.app_name + "/.git; fi"
        cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)
        if self.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(cmdline)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(cmdline)
        return rc

    def clone_data_repo(self):
        """Clone the application's GIT repo."""
        if self.git_data_url:
            logging.info("Cloning data GIT repo on %s", self.machine)
            target_branch, git_url = self.generate_git_url_branch(self.git_data_branch, self.git_data_url,
                                                                  self.git_data_user, self.git_data_token)
            cmdline = "cd " + self.get_workdir("dataset") + \
               f" && echo -n {self.dataset_label} > dataset_label.txt" + \
                " && if [[ ! -d " + self.app_name + " ]]; then" + \
                " git clone --no-checkout -b " + target_branch + \
                " " + git_url + " " + self.app_name + \
                " && cd "+self.app_name + \
               f" && git sparse-checkout set {self.git_data_download_path}" + \
                " && git checkout"+ \
                " && rm -rf .git; fi"
        else:
            logging.info("Making empty data directory on %s", self.machine)
            cmdline = "cd " + self.get_workdir("dataset") + \
               f" && echo -n {self.dataset_label} > dataset_label.txt" + \
                " && if [[ ! -d " + self.app_name + " ]]; then" + \
               f" mkdir {self.app_name}; fi"
        cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)
        if self.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(cmdline)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(cmdline)
        return rc

    def copy_data_from_fs(self):
        """Copy extra data from local FS."""
        rc = 0
        if self.git_data_copy_from_fs:
            logging.info("Copying extra data from local FS on %s", self.machine)
            data_dir = self.get_workdir("dataset") + "/" + self.app_name
            cmdline = "cd " + data_dir
            if self.git_data_download_path:
                cmdline += " && if [[ -f " + self.git_data_download_path + " ]]; then" + \
                           " cp -rfL " + self.git_data_copy_from_fs + "/* $(dirname " + self.git_data_download_path + "\);" \
                           " else  cp -rfL " + self.git_data_copy_from_fs + "/*" + self.git_data_download_path + ";fi'"
            else:
                cmdline += " && cp -rfL " + self.git_data_copy_from_fs + "/* ./"
            cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)
            if self.remote_job:
                rc, cmdout = cmd_runner.run_remote_cmd(cmdline)
            else:
                rc, cmdout = cmd_runner.run_local_cmd(cmdline)
        return rc

    def generate_git_url_branch(self, branch, url, user, token):
        if branch == None:
            branch = "master"
        if user:
            credential = f'{urllib.parse.quote(user, safe="")}:{token}'
            url = url.replace('://', f'://{credential}@')
        return branch, url

    def retrieve_results(self, in_container):
        ov_run_dir = self.get_workdir("oneview_runs")
        ov_name = "oneview_runs"
        gz_file = f"{ov_name}.tar.gz"
        remote_gz_file = f"/tmp/{gz_file}"
        local_out_dir = os.path.join(self.launch_output_dir, ov_name)

        cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)

        tar_cmd = f"cd {ov_run_dir} && tar --ignore-failed-read -czvf {remote_gz_file} $(find ./ -name \"oneview_results*\") ../qaas_reports"
        if self.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(tar_cmd)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(tar_cmd)
        if rc != 0:
            return rc

        os.makedirs(local_out_dir, exist_ok=True)

        if self.remote_job:
            rc, cmdout = cmd_runner.copy_remote_file(remote_gz_file, local_out_dir)
        else:
            rc, cmdout = cmd_runner.copy_local_file(remote_gz_file, local_out_dir)
        if rc != 0:
            return rc

        untar_cmd = f"cd {local_out_dir} && tar xvfz {gz_file}"
        rc, cmdout = cmd_runner.run_local_cmd(untar_cmd)
        if rc != 0:
            return rc

        self.package_data(in_container)

        rm_gz_cmd = f"rm -f {remote_gz_file}"
        if self.remote_job:
            rc, cmdout = cmd_runner.run_remote_cmd(rm_gz_cmd)
        else:
            rc, cmdout = cmd_runner.run_local_cmd(rm_gz_cmd)
        return rc

    def finish(self):
        if self.remote_job:
            self.msg_server.shutdown()



    def package_data(self, in_container):
        local_out_dir = self.launch_output_dir
        reorg_local_out_dir=os.path.join(local_out_dir, 'reorg', os.path.basename(local_out_dir))
        real_qaas_data_root=os.path.join(local_out_dir, "oneview_runs")
        qaas_reports_folder=os.path.join(real_qaas_data_root, "qaas_reports")
        ov_folder_for_best_compilers=os.path.join(real_qaas_data_root, "compilers")
        ov_folder_for_default=os.path.join(real_qaas_data_root, "defaults")

        os.makedirs(reorg_local_out_dir, exist_ok=True)
        for compiler_folder in os.listdir(qaas_reports_folder):
            shutil.copy(os.path.join(qaas_reports_folder, compiler_folder), reorg_local_out_dir)
        out_oneview_folders=os.path.join(reorg_local_out_dir, "oneview_runs")

        compilers=[]
        compiler_options=[]
        folders=[]

        self.process_oneview_data(ov_folder_for_best_compilers, out_oneview_folders, compilers, compiler_options, folders, lambda folder: folder.split("_")+[folder], in_container)
        self.process_oneview_data(ov_folder_for_default, out_oneview_folders, compilers, compiler_options, folders, lambda folder: [folder, 0, f'{folder}_default'], in_container)

        ov_folders_info_df = pd.DataFrame({"compiler":compilers, "option #":compiler_options, "ov_folder":folders})
        #print(ov_folders_info_df)

    # Now add the ov_folder column to data
    # This is for multi-compiler data
        multi_compiler_data_fn = os.path.join(reorg_local_out_dir, 'qaas_compilers.csv')
        multi_compiler_data_df = pd.read_csv(multi_compiler_data_fn)
        result = pd.merge(multi_compiler_data_df, ov_folders_info_df, on=['compiler', 'option #'], how='left')
        #print(result)
        result.to_csv(multi_compiler_data_fn, index=False)
        #print(reorg_local_out_dir)
        reorg_local_dir_name = os.path.basename(reorg_local_out_dir)
        with tarfile.open(os.path.join('/tmp/qaas_out.tar.gz'), 'w:gz') as tar:
            tar.add(reorg_local_out_dir, arcname=reorg_local_dir_name)
        with tarfile.open(os.path.join('/tmp/qaas_out-debug.tar.gz'), 'w:gz') as tar:
            tar.add(reorg_local_out_dir, arcname=reorg_local_dir_name)
        with open("/tmp/debug-tar.txt", "w") as f: f.write(f'{reorg_local_out_dir}, {reorg_local_dir_name}')

    def process_oneview_data(self, ov_folder_to_extract, out_oneview_folders, compilers, compiler_options, folders, 
                            parse_compiler_folder_name_fn, in_container):
        if not os.path.exists(ov_folder_to_extract):
            return # Skip if ov folder not exist
        for compiler_folder in os.listdir(ov_folder_to_extract):
            #print(compiler_folder)
            in_path=os.path.join(ov_folder_to_extract, compiler_folder)
        # Need to go one more level to get the real oneview folder
            in_oneview_folder = os.listdir(in_path)
            assert(len(in_oneview_folder)==1)
            in_oneview_folder = in_oneview_folder[0]
            full_in_oneview_folder = os.path.join(ov_folder_to_extract, compiler_folder, in_oneview_folder)

            compiler_folder_parts = parse_compiler_folder_name_fn(compiler_folder)
            compiler, option_num, out_compiler_folder = compiler_folder_parts

            full_out_oneview_folder=os.path.join(out_oneview_folders, out_compiler_folder, in_oneview_folder)

            compilers.append(compiler)
            compiler_options.append(int(option_num))
            folders.append(os.path.relpath(full_out_oneview_folder, out_oneview_folders))
            script_dir = self.get_script_root(in_container)
            ov_backend_path = os.path.join(script_dir, "qaas-web", "apps", "oneview", "backend")
            # Try to add script path temporarily.   
            # Similar to run_job() in job_submit.py but not running function as separate script.
            original_sys_path = sys.path.copy()
            sys.path.insert(0, ov_backend_path)
            # following import requires qaas-web/apps/oneview/backend in PYTHONPATH
            from ov_file_extractor_db import extract_ov_file
            sys.path = original_sys_path
            extract_ov_file(full_in_oneview_folder, full_out_oneview_folder)

#TEST_LOCAL_OUT_DIR="/nfs/site/proj/alac/tmp/qaas_out-amg/tmp/qaas_out-test/170-852-0034"
#TEST_LOCAL_OUT_DIR="/tmp/qaas_out/170-909-9726-test"
#package_data(TEST_LOCAL_OUT_DIR)
