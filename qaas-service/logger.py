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
# Contributors: David/Hafid

from enum import Enum, auto

class Color(Enum):
    RED = '\033[31m'
    RESET = '\033[39;49m'
    BLACK = '\033[30m'
    GREEN = '\033[32m'
    ORANGE = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    LIGHTGREY = '\033[37m'
    DARKGREY = '\033[90m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    YELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    PINK = '\033[95m'
    LIGHTCYAN = '\033[96m'
    WHITE = '\033[37m'

class QaasComponents(Enum):
    APP_BUILDER = Color.GREEN
    APP_MUTATOR = Color.ORANGE
    APP_RUNNER = Color.BLUE
    DB_POPULATOR = Color.PURPLE
    ENV_PROVISIONER = Color.CYAN
    OV_RUNNER = Color.YELLOW
    RESULT_PRESENTER = Color.PINK
    BUSINESS_LOGICS = Color.RED





def log(component, msg, mockup=False):
    prefix = f'{Color.WHITE.value}[MOCKUP]:{Color.RESET.value}' if mockup else ''
    component_color = component.value
    print(f'{prefix} {component_color.value}{msg}{Color.RESET.value}')
