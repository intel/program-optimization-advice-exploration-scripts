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
    def __init__(self, system_compilers, user_compiler, provisioner):
        self.compiler = user_compiler
        self.compilers = system_compilers
        self.provisioner = provisioner

    def build_default(self):
        """Run build stage."""
        logging.info("Build %s using default compiler settings on %s", self.provisioner.app_name, self.provisioner.machine)
        build_cmd = "\"podman run --rm --name " + self.provisioner.app_name + \
                    " -v /home/qaas/DEMO/scripts/app_builder.py:/qaas/app_builder.py" + \
                    " -v " + self.compilers["QAAS_INTEL_COMPILERS_DIRECTORY"] + ":/opt/intel/oneapi" + \
                    " -v " + self.compilers["QAAS_GNU_COMPILERS_DIRECTORY"] + ":/opt/gnu" + \
                    " -v " + self.provisioner.get_workdir("build") + ":/app/builder" + \
                    " " + self.provisioner.image_name + " /usr/bin/python3 /qaas/app_builder.py" + \
                    " --src-dir /app/builder/" + self.provisioner.app_name + \
                    " --compiler-dir /opt/intel/oneapi/" + \
                    " --relative-binary-path builder/build/bin/miniQMC" + \
                    " --orig-user-CC='" + self.compiler["USER_CC"] + "'" + \
                    " --target-CC='" + self.compiler["USER_CC"] + "'" + \
                    " --user-c-flags='" + self.compiler["USER_C_FLAGS"] + "'" + \
                    " --user-cxx-flags='" + self.compiler["USER_CXX_FLAGS"] + "'" + \
                    " --user-fc-flags='" + self.compiler["USER_FC_FLAGS"] + "'" + \
                    " --user-link-flags='" + self.compiler["USER_LINK_FLAGS"] + "'" + \
                    " --user-target='" + self.compiler["USER_TARGET"] + "'\""
        logging.debug("build_cmd=%s", build_cmd)
        rc = 0
        rc, cmdout = QAASRunCMD(self.provisioner.machine).run_remote_cmd(build_cmd)
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
