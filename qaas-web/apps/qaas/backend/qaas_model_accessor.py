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
# Contributors: Yue/David
from util import *
import os
import pandas as pd
import shutil
import sys
import pandas as pd
current_directory = os.path.dirname(os.path.abspath(__file__))
base_directory = os.path.join(current_directory, '../../common/backend/')
base_directory = os.path.normpath(base_directory)  
sys.path.insert(0, base_directory)
from model_accessor_base import ModelAccessor
from model_collection import *
from base_util import *

class QaaSModelInitializer(ModelAccessor):
    def __init__(self, session, qaas_data_file_path):
        super().__init__(session)
        self.qaas_data_file_path = qaas_data_file_path
        self.current_row = None
    def visitQaaSDataBase(self, qaas_database):
        df = read_file(self.qaas_data_file_path, delimiter=',')
        #iterate file each row in the file is new execution
        for index, row in df.iterrows():
            self.current_row = row
            current_application = Application(self)
            current_execution = Execution(self)
            ### set the execution 
            self.current_execution = current_execution
            current_execution.application = current_application
            qaas_database.add_to_data_list(current_execution)
                   
   
    def visitApplication(self, application):
        app_name = self.current_row['app_name']
        application.workload = app_name
        
    def visitExecution(self, execution):
        execution.time = self.current_row['time(s)']
        compiler_vendor = self.current_row['compiler']
        compiler_flag = self.current_row['flags']
        compiler = Compiler.get_or_create_compiler_by_compiler_info(vendor=compiler_vendor, version=None, initializer=self)
        compiler_option = CompilerOption.get_or_create_compiler_option(compiler_flag, self)
        compiler_option.compiler = compiler

    def visitQaaS(self, qaas):
        pass
    def visitEnvironment(self, environment):
        pass
    def visitOs(self, os):
        pass
    def visitHwSystem(self, hwsystem):
        pass
    def visitMaqao(self, maqao):
        pass
    def visitCompilerCollection(self, compiler_collection):
        pass
    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        pass
    def visitModuleCollection(self, module_collection):
        pass
    def visitBlockCollection(self, block_collection):
        pass
    def visitFunctionCollection(self, function_collection):
        pass
    def visitLoopCollection(self, loop_collection):
        pass
    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        pass
    def visitCqaCollection(self, cqa_collection):
        pass
    def visitAsmCollection(self, asm_collection):
        pass
    def visitGroupCollection(self, group_collection):
        pass
    def visitSourceCollection(self, source_collection):
        pass


