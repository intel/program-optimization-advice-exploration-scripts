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
from utils.runcmd import QAASRunCMD

# define QAAS GIT-related constants
GIT_USER = "USER"
GIT_TOKEN = "TOKEN"
GIT_BRANCH = "BRANCH"
GIT_SRC_URL = "SRC_URL"
GIT_DATA_URL = "DATA_URL"

# define directory structure constants
WORKDIR_ROOT_INDEX  = 0
BUILDDIR_INDEX      = 1
RUNDIR_INDEX        = 2
BASEDIR_INDEX       = 3
OVDIR_INDEX         = 4
LOCUSDIR_INDEX      = 5
QAAS_RUN_TYPES = ["base_runs", "oneview_runs", "locus_runs"]

class QAASEnvProvisioner:
    """Object to manage environment setup."""
    def __init__(self, service_dir, account, app_name, git_params, machine, container):
        logging.debug("QAASEnvProvisioner Constructor")
        # save mete information
        self.service_dir = service_dir
        self.account = account
        self.app_name = app_name
        # setup working directories
        self.work_dirs = []
        self.work_dirs.append(os.path.join(self.service_dir, self.account, self.app_name))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "build"))
        self.work_dirs.append(os.path.join(self.work_dirs[WORKDIR_ROOT_INDEX], "run"))
        for workdir in QAAS_RUN_TYPES:
            self.work_dirs.append(os.path.join(self.work_dirs[RUNDIR_INDEX], workdir))
        # save git configuration
        self.git_user = git_params[GIT_USER]
        self.git_token = git_params[GIT_TOKEN]
        self.git_branch = git_params[GIT_BRANCH]
        self.git_src_url = git_params[GIT_SRC_URL]
        self.git_data_url = git_params[GIT_DATA_URL]
        # save target machine access parameters
        self.machine = machine
        self.image_name = container["QAAS_CONTAINER_IMAGE"] + ":" + container["QAAS_CONTAINER_TAG"]
        self.image_uid = container["QAAS_CONTAINER_UID"]

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

    def create_work_dirs(self):
        """Create working directories."""
        logging.info("Create Working Directories on %s", self.machine)
        # craete dirs
        cmds = "'" + "mkdir -p " + self.work_dirs[0]
        for index in range(1, len(self.work_dirs), 1): 
            cmds = cmds + " && " + "mkdir -p " + self.work_dirs[index]
        cmds = cmds + "'"
        rc, cmdout = QAASRunCMD(self.machine).run_remote_cmd(cmds)
        if rc != 0:
            return rc
        # update ownership rights for container runs 
        rc = self.update_workdir_owner()
        return rc

    def update_workdir_owner(self):
        """Update working directories ownership rights to build & run in a container."""
        cmdline = "podman unshare chown -R :" + self.image_uid + " " + self.get_workdir("root")
        rc, cmdout = QAASRunCMD(self.machine).run_remote_cmd(cmdline)
        return rc

    def clone_source_repo(self):
        """Clone the application's GIT repo."""
        logging.info("Cloning application GIT repo on %s", self.machine)
        target_branch = self.git_branch
        if self.git_branch == None:
            target_branch = "master"
        cmdline = "'cd " + self.get_workdir("build") + \
                  " && if [[ ! -d " + self.app_name + " ]]; then" + \
                  " git clone -b " + target_branch + \
                  " " + self.git_src_url + " " + self.app_name + \
                  " && rm -rf " + self.app_name + "/.git; fi'"
        rc, cmdout = QAASRunCMD(self.machine).run_remote_cmd(cmdline)
        return rc
