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

    # Check whether to disable container mode
    container = True if not args.no_container else False

    # Check whether to map root user in container to host user user (preserves name space)
    user_ns_root = False if not args.as_root_in_container else True

    # Command line just print the message for service message, GUI will act on message differently.
    rc, _ = launch_qaas(args.app_params, args.logic, not args.local_job,
                        container, user_ns_root,
                        args.no_compiler_default, args.no_compiler_flags,
                        args.parallel_compiler_runs, args.enable_parallel_scale,
                        lambda msg: print(msg.str()))

    exitcode = 1
    if rc == 0:
        exitcode = 0
    logging.debug("exitcode = %s", exitcode)
    sys.exit(exitcode)

def launch_qaas_web(qaas_message_queue, app_params, launch_output_dir='/tmp/qaas_out'):
   launch_qaas(app_params, "demo", True, True, False, False, False, "off", False, lambda msg: qaas_message_queue.put(msg), launch_output_dir)

# Webfront will call this to launch qaas for a submission
def launch_qaas(app_params, logic, remote_job,
                container, user_ns_root,
                no_compiler_default, no_compiler_flags,
                parallel_compiler_runs, enable_parallel_scale,
                service_msg_recv_handler, launch_output_dir='/tmp/qaas_out'):
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
    # check if runtime section is added
    if "runtime" not in params.user.keys():
        params.user["runtime"] = {"MPI":"no", "OPENMP":"no"}
    logging.debug("QaaS User Config:\n\t%s", params.user)

    if user_ns_root and params.system["machines"]["QAAS_USER"] == "root":
        logging.error("Run as root in container not allowed for QAAS_USER=root\n")
        return 1,None

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
                              params.system["analyzers"],
                              params.system["global"]["QAAS_COMM_PORT"],
                              remote_job,
                              service_msg_recv_handler,
                              launch_output_dir)
    rc = prov.create_work_dirs(container, user_ns_root)
    if rc != 0:
       return rc
    rc = prov.clone_source_repo()
    if rc != 0:
       return rc

    rc = prov.clone_data_repo()
    if rc != 0:
       return rc

    rc = prov.copy_data_from_fs()
    if rc != 0:
       return rc

    # setup job submission
    job = QAASJobSubmit(params.system["compilers"],
                        params.user["compiler"],
                        params.user["application"],
                        params.user["runtime"],
                        prov,
                        logic,
                        no_compiler_default,
                        no_compiler_flags,
                        parallel_compiler_runs,
                        enable_parallel_scale)

    rc = job.run_job(container, user_ns_root)
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
