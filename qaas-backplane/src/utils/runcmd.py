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
# Created October 2022
# Contributors: Hafid/David

import os
import sys
import logging
import subprocess

# constants
DEFAULT_USER = 'qaas'
DEFAULT_SSH_PORT = '10022'
DEFAULT_LOCATION = 'localhost'

class QAASRunCMD:
    def __init__(self, comm_port, machine=DEFAULT_LOCATION, ssh_port=DEFAULT_SSH_PORT, user=DEFAULT_USER):
        self.machine = machine
        self.ssh_port = ssh_port
        self.user = user
        # Use remote port forwarding and then local side listen to the forwarding port, expecting remote side connect back
        self.ssh_cmd = f"/usr/bin/ssh -p {self.ssh_port} -R {comm_port}:localhost:{comm_port} " + self.user + "@" + self.machine + " "

    def run_cmd(self, cmdline):
        runcmd = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        runcmd.out, runcmd.err = runcmd.communicate()
        if runcmd.returncode != 0:
             logging.error(runcmd.err.decode("utf-8"))
             logging.debug(runcmd.out.decode("utf-8"))
        return runcmd.returncode, runcmd.out.decode("utf-8")

    def copy_local_file(self, local_file, local_dir):
        cp_cmd = f"/usr/bin/cp {local_file} {local_dir}"
        logging.debug("cmdline=%s", cp_cmd)
        rc, cmdout = self.run_cmd(cp_cmd)
        return rc, cmdout

    def copy_remote_file(self, remote_file, local_dir):
        scp_cmd = f"/usr/bin/scp -P {self.ssh_port} " + self.user + "@" + self.machine + f":{remote_file} {local_dir}"
        logging.debug("cmdline=%s", scp_cmd)
        rc, cmdout = self.run_cmd(scp_cmd)
        return rc, cmdout
    
    def run_local_cmd(self, local_cmd):
        """Run a local command."""
        cmdline = "/usr/bin/bash -c " + local_cmd
        logging.debug("cmdline=%s", cmdline)
        rc, cmdout = self.run_cmd(cmdline)
        return rc, cmdout

    def run_remote_cmd(self, remote_cmd):    
        """Run a remote command over ssh."""
        cmdline = self.ssh_cmd + " " + remote_cmd
        logging.debug("cmdline=%s", cmdline)
        rc, cmdout = self.run_cmd(cmdline)
        return rc, cmdout
