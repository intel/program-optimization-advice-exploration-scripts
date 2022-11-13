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

# define constants

compiler_subdir_map = { 'icc:2022': 'intel/2022', 'icc:19.1': 'intel/19.1',
                       'icx:2022': 'intel/2022', 'icx:19.1': 'intel/19.1',
                       'gcc:11.1': 'gcc/gcc-11.1', 'gcc:11.1': 'gcc/gcc-11.1' }

class QAASJobSubmit:
    """."""
    def __init__(self, system_compilers, user_compiler, user_application, provisioner):
        self.compiler = user_compiler
        self.compilers = system_compilers
        self.provisioner = provisioner
        self.application = user_application

    def build_default(self):
        """Run build stage."""
        logging.info("Build %s using default compiler settings on %s", self.provisioner.app_name, self.provisioner.machine)
        build_cmd = "\"podman run --rm --name " + self.provisioner.app_name + \
                    " -v /home/qaas/DEMO/scripts/app_builder.py:/qaas/app_builder.py" + \
                    " -v /home/qaas/DEMO/scripts/util.py:/qaas/util.py" + \
                    " -v " + self.compilers["QAAS_INTEL_COMPILERS_DIRECTORY"] + ":/opt/intel/oneapi" + \
                    " -v " + self.compilers["QAAS_GNU_COMPILERS_DIRECTORY"] + ":/opt/gnu" + \
                    " -v " + self.provisioner.get_workdir("build") + ":/app/builder" + \
                    " " + self.provisioner.image_name + " /usr/bin/python3 /qaas/app_builder.py" + \
                    " --src-dir /app/builder/" + self.provisioner.app_name + \
                    " --compiler-dir /opt/intel/oneapi/" + \
                    " --output-binary-path builder/build/bin/miniQMC" + \
                    " --orig-user-CC='" + self.compiler["USER_CC"] + "'" + \
                    " --target-CC='" + self.compiler["USER_CC"] + "'" + \
                    " --user-c-flags='" + self.compiler["USER_C_FLAGS"] + "'" + \
                    " --user-cxx-flags='" + self.compiler["USER_CXX_FLAGS"] + "'" + \
                    " --user-fc-flags='" + self.compiler["USER_FC_FLAGS"] + "'" + \
                    " --user-link-flags='" + self.compiler["USER_LINK_FLAGS"] + "'" + \
                    " --user-target='" + self.compiler["USER_TARGET"] + "'" + \
                    " --user-target-location='/app/builder/build/" + self.compiler["USER_TARGET_LOCATION"] + "'" + \
                    " --mode=both" + "\""
        logging.debug("build_cmd=%s", build_cmd)
        rc = 0
        rc, cmdout = QAASRunCMD(self.provisioner.machine).run_remote_cmd(build_cmd)
        if rc == 0:
            logging.debug(cmdout)
        return rc

    def run_job(self):
        """Run job script itself"""
        script_root = self.provisioner.script_root
        compiler_root = self.provisioner.get_compiler_root()
        compiler_subdir = self.provisioner.get_compiler_subdir(self.compiler["USER_CC"], self.compiler["USER_CC_VERSION"])
        ov_run_dir = self.provisioner.get_workdir("oneview_runs")
        locus_run_dir = self.provisioner.get_workdir("locus_runs")
        ov_dir="/opt/maqao"
        container_app_builder_path="/app/builder"
        container_app_dataset_path="/app/dataset"
        container_app_oneview_path="/app/oneview_runs"
        container_app_locus_path="/app/locus_runs"
        #container_compiler_root="/app/compilers"
        # The current load script seems to require the same path
        container_compiler_root=compiler_root
        container_script_root="/app/QAAS_SCRIPT_ROOT"
        app_run_info = self.application["RUN"]
        env_var_map=app_run_info["APP_ENV_MAP"]
        env_var_flags = "".join([f' --var {k}={v}' for k,v in env_var_map.items()])
        # Below used --network=host so script can communicate back to launcher via ssh forwarding.  Can try to restrict to self.provisioner.comm_port if needed
        job_cmd = "'podman run --rm --name " + self.provisioner.app_name + \
                    " --network=host " + \
                   f" -v {ov_dir}:{ov_dir}" + \
                   f" -v {script_root}:{container_script_root}" + \
                    " -v " + self.provisioner.get_workdir("build") + f":{container_app_builder_path}" + \
                    " -v " + ov_run_dir + f":{container_app_oneview_path}" + \
                    " -v " + locus_run_dir + f":{container_app_locus_path}" + \
                    " -v " + compiler_root + f":{container_compiler_root}" + \
                    " -v " + os.path.join(self.provisioner.get_workdir("dataset"), self.provisioner.app_name) + f":{container_app_dataset_path}" + \
                    " --cap-add  SYS_ADMIN,SYS_PTRACE" + \
                    " " + self.provisioner.image_name + f" /usr/bin/python3 {container_script_root}/qaas-service/job.py "+ \
                    f' --src-dir {os.path.join(container_app_builder_path, self.provisioner.app_name)}'+ \
                    f' --data_dir {os.path.join(container_app_dataset_path, self.provisioner.git_data_download_path)} --ov_config unused --ov_run_dir {container_app_oneview_path}'+ \
                    f' --locus_run_dir {container_app_locus_path} --compiler-dir {os.path.join(container_compiler_root, compiler_subdir)} --ov_dir {ov_dir}'+ \
                    f' --orig-user-CC {self.compiler["USER_CC"]} --target-CC {self.compiler["USER_CC"]} --user-c-flags "{self.compiler["USER_C_FLAGS"]}"'+ \
                    f' --user-cxx-flags "{self.compiler["USER_CXX_FLAGS"]}" --user-fc-flags "{self.compiler["USER_FC_FLAGS"]}"'+ \
                    f' --user-link-flags "{self.compiler["USER_LINK_FLAGS"]}" --user-target {self.compiler["USER_TARGET"]} --user-target-location {self.compiler["USER_TARGET_LOCATION"]}'+ \
                    f'{env_var_flags}'+ \
                    f' --run-cmd "{app_run_info["APP_RUN_CMD"]}"' + \
                    f" --comm-port {self.provisioner.comm_port}" + \
                    "'" 
        
        logging.debug("job_cmd=%s", job_cmd)
        rc = 0
        rc, cmdout = QAASRunCMD(self.provisioner.comm_port, self.provisioner.machine).run_remote_cmd(job_cmd)
        if rc == 0:
            logging.debug(cmdout)
        return rc
    
    def run_reference_app(self):
        """Run a reference run of the application."""
        logging.info("Run a reference run of %s on %s", self.provisioner.app_name, self.provisioner.machine)
        # NOTE: temporarly run the following until app_runner inetgration
        run_cmd = "\"{ " + \
                  "printf '#!/bin/bash\\n\\nRANKS=\$(nproc)\\nif [[ ! -z \\\"\$1\\\"  ]]; then RANKS=\$1; fi\\n\\n'" + \
                  " && printf 'source /opt/intel/oneapi/setvars.sh >/dev/null\\n'" + \
                  " && printf 'export OMP_NUM_THREADS=1\\nexport I_MPI_PIN_PROCESSOR_LIST=\\\"all:map=spread\\\"\\n'" + \
                  " && printf '/opt/maqao/bin/maqao oneview -R1 xp=miniqmc-mpi --replace --mpi_command=\\\"mpirun -np \$RANKS\\\" -- '" + \
                  " && printf '/app/builder/build/bin/miniqmc -g \\\"2 2 2\\\" -b\\n'" + \
                  " ; } > " + self.provisioner.get_workdir("base_runs") + "/run.sh" + \
                  " ; chmod ug+x " + self.provisioner.get_workdir("base_runs") + "/run.sh\""
        logging.debug("run_cmd=%s", run_cmd)
        rc = 0
        rc, cmdout = QAASRunCMD(self.provisioner.machine).run_remote_cmd(run_cmd)
        if rc != 0:
            return rc
        logging.debug(cmdout)
        run_cmd = "\"podman run --rm --name " + self.provisioner.app_name + \
                  " -v /opt/maqao:/opt/maqao" + \
                  " -v " + self.compilers["QAAS_INTEL_COMPILERS_DIRECTORY"] + ":/opt/intel/oneapi" + \
                  " -v " + self.compilers["QAAS_GNU_COMPILERS_DIRECTORY"] + ":/opt/gnu" + \
                  " -v " + self.provisioner.get_workdir("build") + ":/app/builder" + \
                  " -v " + self.provisioner.get_workdir("base_runs") + ":/app/runner" + \
                  " --cap-add  SYS_ADMIN,SYS_PTRACE" + \
                  " " + self.provisioner.image_name + " /app/runner/run.sh 8\""
        logging.debug("run_cmd=%s", run_cmd)
        rc = 0
        rc, cmdout = QAASRunCMD(self.provisioner.machine).run_remote_cmd(run_cmd)
        if rc == 0:
            logging.debug(cmdout)
        return rc 
