#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# TO BE FIXED
# Copyright (C) 2022  Intel Corporation  All rights reserved
###############################################################################
# HISTORY
# Created October 2022
# Contributors: Hafid/David

import os
import sys
import logging
import subprocess

# constants
DEFAULT_USER = 'qaas'
DEFAULT_LOCATION= 'localhost'

class QAASRunCMD:
    def __init__(self, comm_port, machine=DEFAULT_LOCATION, user=DEFAULT_USER):
        self.machine = machine
        self.user = user
        # Use remote port forwarding and then local side listen to the forwarding port, expecting remote side connect back
        self.ssh_cmd = f"/usr/bin/ssh -R {comm_port}:localhost:{comm_port} " + self.user + "@" + self.machine + " "

    def run_cmd(self, cmdline):
        runcmd = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        runcmd.out, runcmd.err = runcmd.communicate()
        if runcmd.returncode != 0:
             logging.error(runcmd.err)
        return runcmd.returncode, runcmd.out

    def copy_remote_file(self, remote_file, local_dir):
        scp_cmd = f"/usr/bin/scp " + self.user + "@" + self.machine + f":{remote_file} {local_dir}"
        logging.debug("cmdline=%s", scp_cmd)
        rc, cmdout = self.run_cmd(scp_cmd)
        return rc, cmdout
    
    def run_local_cmd(self, local_cmd):
        """Run a local command."""
        cmdline = local_cmd
        logging.debug("cmdline=%s", cmdline)
        rc, cmdout = self.run_cmd(cmdline)
        return rc, cmdout

    def run_remote_cmd(self, remote_cmd):    
        """Run a remote command over ssh."""
        cmdline = self.ssh_cmd + " " + remote_cmd
        logging.debug("cmdline=%s", cmdline)
        rc, cmdout = self.run_cmd(cmdline)
        return rc, cmdout
