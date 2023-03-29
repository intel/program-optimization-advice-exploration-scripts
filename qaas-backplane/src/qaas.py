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
from multiprocessing import Process, Queue
from utils import qaas_message as qm
#import database_populator
#import result_presenter

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    """QaaS Script Entry Point."""

    # parse arguments
    args = utils.cmdargs.parse_cli_args(sys.argv)

    # Command line just print the message for service message, GUI will act on message differently.
    rc, _ = launch_qaas(args.app_params, args.logic, lambda msg: print(msg.str()))

    exitcode = 1
    if rc == 0:
        exitcode = 0
    logging.debug("exitcode = %s", exitcode)
    sys.exit(exitcode)

def launch_qaas_web(qaas_message_queue, app_params, launch_output_dir='/tmp/qaas_out'):
   launch_qaas(app_params, "demo", lambda msg: qaas_message_queue.put(msg), launch_output_dir)

# Webfront will call this to launch qaas for a submission
def launch_qaas(app_params, logic, service_msg_recv_handler, launch_output_dir='/tmp/qaas_out'):
    # Better api to send back message 
    service_msg_recv_handler(qm.BeginQaas())
    # setup QaaS configuration
    script_dir=os.path.dirname(os.path.realpath(__file__))
    params = utils.config.QAASConfig(config_file_path=os.path.join(script_dir, "../config/qaas.conf"))
    # get QaaS global configuration
    params.read_system_config()
    logging.debug("QaaS System Config:\n\t%s", params.system)
    # get QaaS user's configuration
    params.read_user_config(app_params)
    logging.debug("QaaS User Config:\n\t%s", params.user)
    
    # Setup Env. Provisionning: code  + data location
    prov = QAASEnvProvisioner(params.system["global"]["QAAS_ROOT"], 
                              params.system["global"]["QAAS_SCRIPT_ROOT"], 
                              params.user["account"]["QAAS_ACCOUNT"], 
                              params.user["application"]["APP_NAME"], 
                              params.user["application"]["GIT"],
                              params.system["machines"],
                              params.system["container"],
                              params.system["compilers"],
                              params.system["compiler_mappings"],
                              int(params.system["global"]["QAAS_COMM_PORT"]),
                              service_msg_recv_handler,
                              launch_output_dir)
    rc = prov.create_work_dirs(container=False)
    if rc != 0:
       return rc
    rc = prov.clone_source_repo()
    if rc != 0:
       return rc

    rc = prov.clone_data_repo()
    if rc != 0:
       return rc

    # setup job submission
    job = QAASJobSubmit(params.system["compilers"],
                        params.user["compiler"],
                        params.user["application"],
                        prov,
                        logic)

    rc = job.run_job(container=False)
    #rc = job.build_default()
    #rc = job.run_reference_app()
    if rc != 0:
       return rc

    # just for testing
    rc = prov.retrieve_results()
    if rc != 0:
       return rc

    print(f'ov results under: {prov.launch_output_dir}')
    prov.finish()
    service_msg_recv_handler(qm.EndQaas(prov.launch_output_dir))
    return rc, prov.launch_output_dir
     
if __name__ == '__main__':
   main()
