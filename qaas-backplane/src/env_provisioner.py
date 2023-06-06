#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# TO BE FIXED
# Copyright (C) 2022  Intel Corporation  All rights reserved
###############################################################################
# HISTORY
# Created June 2022
# Updated October 2022
# Contributors: Hafid/David

import os
import logging
import urllib.parse
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

# define directory structure constants
WORKDIR_ROOT_INDEX  = 0
BUILDDIR_INDEX      = 1
RUNDIR_INDEX        = 2
BASEDIR_INDEX       = 3
OVDIR_INDEX         = 4
LOCUSDIR_INDEX      = 5
DATADIR_INDEX      = 6
QAAS_RUN_TYPES = ["base_runs", "oneview_runs", "locus_runs"]


class QAASEnvProvisioner:
    """Object to manage environment setup."""
    def __init__(self, service_dir, script_root, account, app_name, git_params, access_params, container,
                 compilers, compiler_mappings, comm_port, service_msg_recv_handler,
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
        self.work_dirs = []
        self.work_dirs.append(os.path.join(self.service_dir, self.account, self.app_name))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "build"))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "run"))
        for workdir in QAAS_RUN_TYPES:
            self.work_dirs.append(os.path.join(self.work_dirs[RUNDIR_INDEX], workdir))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "dataset"))
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
        # save target machine access parameters
        self.user = access_params["QAAS_USER"]
        self.ssh_port = access_params["QAAS_SSH_PORT"]
        self.machine = access_params["QAAS_MACHINES_POOL"]
        self.image_name = container["QAAS_CONTAINER_IMAGE"] + ":" + container["QAAS_CONTAINER_TAG"]
        self.image_uid = container["QAAS_CONTAINER_UID"]
        self.comm_port = comm_port
        self.msg_server = ServiceMessageReceiver(("localhost", self.comm_port), service_msg_recv_handler=service_msg_recv_handler) 
        self.compiler_root = compilers["QAAS_COMPILERS_ROOT_DIRECTORY"]
        self.compiler_mappings = compiler_mappings
        self._launch_output_dir = launch_output_dir

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

    def create_work_dirs(self, container=True):
        """Create working directories."""
        logging.info("Create Working Directories on %s", self.machine)
        # craete dirs
        cmds = "'" + "mkdir -p " + self.work_dirs[0]
        for index in range(1, len(self.work_dirs), 1): 
            cmds = cmds + " && " + "mkdir -p " + self.work_dirs[index]
        cmds = cmds + "'"
        rc, cmdout = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user).run_remote_cmd(cmds)
        if rc != 0:
            return rc
        # update ownership rights for container runs
        if container:
            rc = self.update_workdir_owner()
        return rc

    def update_workdir_owner(self):
        """Update working directories ownership rights to build & run in a container."""
        cmdline = "podman unshare chown -R :" + self.image_uid + " " + self.get_workdir("root")
        rc, cmdout = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user).run_remote_cmd(cmdline)
        return rc

    def clone_source_repo(self):
        """Clone the application's GIT repo."""
        logging.info("Cloning application GIT repo on %s", self.machine)
        target_branch, git_url = self.generate_git_url_branch(self.git_branch, self.git_src_url,
                                                              self.git_user, self.git_token)
        cmdline = "'cd " + self.get_workdir("build") + \
                  " && if [[ ! -d " + self.app_name + " ]]; then" + \
                  " git clone -b " + target_branch + \
                  " " + git_url + " " + self.app_name + \
                  " && cd " + self.app_name + \
                  f" && if [[ -f .gitmodules ]]; then git submodule update --init --recursive; fi" + \
                  " && cd .." + \
                  " && rm -rf " + self.app_name + "/.git; fi'"
        rc, cmdout = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user).run_remote_cmd(cmdline)
        return rc

    def clone_data_repo(self):
        """Clone the application's GIT repo."""
        if self.git_data_url:
            logging.info("Cloning data GIT repo on %s", self.machine)
            target_branch, git_url = self.generate_git_url_branch(self.git_data_branch, self.git_data_url, 
                                                                  self.git_data_user, self.git_data_token)
            cmdline = "'cd " + self.get_workdir("dataset") + \
                " && if [[ ! -d " + self.app_name + " ]]; then" + \
                " git clone --no-checkout -b " + target_branch + \
                " " + git_url + " " + self.app_name + \
                " && cd "+self.app_name + \
               f" && git sparse-checkout set {self.git_data_download_path}" + \
                " && git checkout"+ \
                " && rm -rf .git; fi'" 
        else:
            logging.info("Making empty data directory on %s", self.machine)
            cmdline = "'cd " + self.get_workdir("dataset") + \
                " && if [[ ! -d " + self.app_name + " ]]; then" + \
               f" mkdir {self.app_name}; fi'" 
        rc, cmdout = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user).run_remote_cmd(cmdline)
        return rc

    def copy_data_from_fs(self):
        """Copy extra data from local FS."""
        rc = 0
        if self.git_data_copy_from_fs:
            logging.info("Copying extra data from local FS on %s", self.machine)
            data_dir = self.get_workdir("dataset") + "/" + self.app_name
            cmdline = "'cd " + data_dir
            if self.git_data_download_path:
                cmdline += " && if [[ -f " + self.git_data_download_path + " ]]; then" + \
                           " cp -rf " + self.git_data_copy_from_fs + "/* $(dirname " + self.git_data_download_path + "\);" \
                           " else  cp -rf " + self.git_data_copy_from_fs + "/*" + self.git_data_download_path + ";fi'"
            else:
                cmdline += " && cp -rf " + self.git_data_copy_from_fs + "/* ./'"
                self.git_data_download_path = "./"
            rc, cmdout = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user).run_remote_cmd(cmdline)
        return rc

    def generate_git_url_branch(self, branch, url, user, token):
        if branch == None:
            branch = "master"
        if user:
            credential = f'{urllib.parse.quote(user, safe="")}:{token}'
            url = url.replace('://', f'://{credential}@')
        return branch, url
    
    def retrieve_results(self):
        ov_run_dir = self.get_workdir("oneview_runs")
        ov_name = "oneview_runs"
        gz_file = f"{ov_name}.tar.gz"
        remote_gz_file = f"/tmp/{gz_file}"
        local_out_dir = os.path.join(self.launch_output_dir, ov_name)

        cmd_runner = QAASRunCMD(self.comm_port, self.machine, self.ssh_port, self.user)

        tar_cmd = f"'cd {ov_run_dir} && tar --ignore-failed-read -czvf {remote_gz_file} $(find ./ -name \"oneview_results*\")' ../qaas_reports"
        rc, cmdout = cmd_runner.run_remote_cmd(tar_cmd)
        if rc != 0:
            return rc

        os.makedirs(local_out_dir, exist_ok=True)

        rc, cmdout = cmd_runner.copy_remote_file(remote_gz_file, local_out_dir)
        if rc != 0:
            return rc

        untar_cmd = f"cd {local_out_dir} && tar xvfz {gz_file}"
        rc, cmdout = cmd_runner.run_local_cmd(untar_cmd)
        if rc != 0:
            return rc

        rm_gz_cmd = f"rm -f {remote_gz_file}"
        rc, cmdout = cmd_runner.run_remote_cmd(rm_gz_cmd)
        return rc
    
    def finish(self):
        self.msg_server.shutdown()
