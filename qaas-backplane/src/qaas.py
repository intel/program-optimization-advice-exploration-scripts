#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# TO BE FIXED
# Copyright (C) 2022  Intel Corporation  All rights reserved
###############################################################################
# HISTORY
# Created June 2022
# Contributors: Hafid/David

"""QAAS CLI."""

import os
import sys
import json
import logging 
import utils.config
import utils.cmdargs
from utils.runcmd import QAASRunCMD
from env_provisioner import QAASEnvProvisioner
from job_submit import QAASJobSubmit
import database_populator
import result_presenter

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    """QaaS Script Entry Point."""

    # parse arguments
    args = utils.cmdargs.parse_cli_args(sys.argv)

    # setup QaaS configuration
    params = utils.config.QAASConfig(config_file_path="../config/qaas.conf")
    # get QaaS global configuration
    params.read_system_config()
    logging.debug("QaaS System Config:\n\t%s", params.system)
    # get QaaS user's configuration
    params.read_user_config(args.app_params)
    logging.debug("QaaS User Config:\n\t%s", params.user)

    # Setup Env. Provisionning: code  + data location
    prov = QAASEnvProvisioner(params.system["global"]["QAAS_ROOT"], 
                              params.user["account"]["QAAS_ACCOUNT"], 
                              params.user["application"]["APP_NAME"], 
                              params.user["application"]["GIT"],
                              params.system["machines"]["QAAS_MACHINES_POOL"],
                              params.system["container"])
    rc = prov.create_work_dirs()
    if rc != 0:
       return rc
    rc = prov.clone_source_repo()
    if rc != 0:
       return rc

    # setup job submission
    job = QAASJobSubmit(params.system["compilers"],
                        params.user["compiler"],
                        prov)
    rc = job.build_default()
    rc = job.run_reference_app()
    if rc != 0:
       return rc

    return rc
     
if __name__ == '__main__':
    rc = main()
    exitcode = 1
    if rc == 0:
        exitcode = 0
    logging.debug("exitcode = %s", exitcode)
    sys.exit(exitcode)
