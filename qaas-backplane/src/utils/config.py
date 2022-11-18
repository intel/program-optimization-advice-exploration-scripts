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
