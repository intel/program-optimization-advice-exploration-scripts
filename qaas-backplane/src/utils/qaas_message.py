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

import pickle
import socket

class QaasMessage:
    def __init__(self, info):
        self.info = info
        self.hostname = socket.gethostname()

    def is_end_job(self):
        return False

    def is_end_qaas(self):
        return False

    def encode(self):
        return pickle.dumps(self)

    def str(self):
        return self.info


class GeneralStatus(QaasMessage):
    def __init__(self, info):
        super().__init__(info)

class BeginJob(QaasMessage):
    def __init__(self):
        super().__init__("Job Begin")

class EndJob(QaasMessage):
    def __init__(self):
        super().__init__("Job End")

    def is_end_job(self):
        return True

class BeginQaas(QaasMessage):
    def __init__(self):
        super().__init__("QAAS Begin")

class EndQaas(QaasMessage):
    def __init__(self, output_ov_dir):
        super().__init__("QAAS End")
        self.output_ov_dir = output_ov_dir

    def is_end_qaas(self):
        return True
