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
    def __init__(self, machine=DEFAULT_LOCATION, user=DEFAULT_USER):
        self.machine = machine
        self.user = user
        self.ssh_cmd = "/usr/bin/ssh " + self.user + "@" + self.machine + " "

    def run_cmd(self, cmdline):
        runcmd = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        runcmd.out, runcmd.err = runcmd.communicate()
        if runcmd.returncode != 0:
             logging.error(runcmd.err)
        return runcmd.returncode, runcmd.out

    def run_local_cmd(cmd, local_cmd):
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
