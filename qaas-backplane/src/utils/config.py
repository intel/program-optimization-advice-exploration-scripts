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
import json
import logging
import configparser

# constants
CONFIG_QAAS = '/etc/qaas.conf'

class QAASConfig:
    def __init__(self, config_file_path=CONFIG_QAAS):
        self.system_config_file = config_file_path
        self.system = dict()
        self.user = dict()

    def read_system_config(self):
        """Read system-wide QaaS configuration."""
        config = configparser.RawConfigParser()
        config.optionxform = str # case-sensitive
        config.read(self.system_config_file, encoding='utf-8')
        # read system-wide variables
        for section in config.sections():
            item = dict()
            for key in config.options(section):
                item[key] = config.get(section, key)
            self.system[section] = item

    def read_user_config(self, user_config_file):
        """Read user specific parameters (JSON) as provided bu GUI."""
        # open JSON user inputs
        with open(user_config_file, "r") as read_file:
            self.user = json.load(read_file)
