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
import os
import pandas as pd
from model_accessor_base import ModelAccessor
from model import *
from model_collection import *
from base_util import *
from oneview_model_accessor import OneViewModelInitializer, OneviewModelAccessor
from qaas_model_accessor import QaaSModelInitializer
   
   
#extends qaas but will intializer a ov intiilzier obj for qaas runs that have ov report
class QaaSOneViewModelInitializer(QaaSModelInitializer, OneViewModelInitializer):
    def __init__(self, session, report_path):
        QaaSModelInitializer.__init__(self, session, report_path)
        self.cur_run_has_ov_data = False
        self.ov_runs_dir = os.path.join(report_path, 'oneview_runs')

    def build_executions_from_file(self, file_path, report_type, qaas_database):
        # read report path
        if os.path.exists(file_path):
            df = read_file(file_path, delimiter=',')
            scalability_reference_line = self.current_metadata_config['SYSTEM'].get('scalability_reference_line')
            self.set_is_baseline(df, scalability_reference_line)

            self.current_type = report_type
            #iterate file each row in the file is new execution
            for index, row in df.iterrows():
                self.current_row = row

                #reset the check later avoid add extra ov info
                if not self.current_row['ov_folder']:
                    self.cur_run_has_ov_data = False
                else:
                    self.cur_run_has_ov_data = True
                    self.set_ov_path(os.path.join(self.ov_runs_dir, self.current_row['ov_folder']))


                self.set_qaas_row_metrics(qaas_database)

                ######################################## OV ########
                ########## oneview specific only set this if there is a ov report associate with this run#########
                if not self.cur_run_has_ov_data:
                    continue
                
                self.set_ov_row_metrics(self.current_execution, qaas_database, self.current_execution.os)

                
                
   
    def visitQaaSDataBase(self, qaas_database):
        QaaSModelInitializer.visitQaaSDataBase(self, qaas_database)

    def visitQaaS(self, qaas):
            pass

    def visitEnvironment(self, environment):
        OneViewModelInitializer.visitEnvironment(self, environment)

    def visitApplication(self, application):
        pass

    def visitExecution(self, execution):
        QaaSModelInitializer.visitExecution(self, execution)

        #only run below if there is ov report avaiable
        if not self.cur_run_has_ov_data:
            return
        OneViewModelInitializer.visitExecution(self, execution)

    def visitOs(self, os):
        #only run below if there is ov report avaiable
        if not self.cur_run_has_ov_data:
            return
        OneViewModelInitializer.visitOs(self, os)

    def visitHwSystem(self, hwsystem):
        #only run below if there is ov report avaiable
        if not self.cur_run_has_ov_data:
            return
        OneViewModelInitializer.visitHwSystem(self, hwsystem)

    def visitMaqao(self, maqao):
        OneViewModelInitializer.visitMaqao(self, maqao)

    def visitDecanCollection(self, decan_collection):
        OneViewModelInitializer.visitDecanCollection(self, decan_collection)

    def visitVprofCollection(self, vprof_collection):
        OneViewModelInitializer.visitVprofCollection(self, vprof_collection)

    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        OneViewModelInitializer.visitLprofCategorizationCollection(self, lprof_categorization_collection)
    
    def visitModuleCollection(self, module_collection):
        OneViewModelInitializer.visitModuleCollection(self, module_collection)

    def visitBlockCollection(self, block_collection):
        OneViewModelInitializer.visitBlockCollection(self, block_collection)

    def visitFunctionCollection(self, function_collection):
        OneViewModelInitializer.visitFunctionCollection(self, function_collection)

    def visitLoopCollection(self, loop_collection):
        OneViewModelInitializer.visitLoopCollection(self, loop_collection)

    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        OneViewModelInitializer.visitLprofMeasurementCollection(self, lprof_measurement_collection)

    def visitCqaCollection(self, cqa_collection):
        OneViewModelInitializer.visitCqaCollection(self, cqa_collection)
    
    def visitAsmCollection(self, asm_collection):
        OneViewModelInitializer.visitAsmCollection(self, asm_collection)

    def visitGroupCollection(self, group_collection):
        OneViewModelInitializer.visitGroupCollection(self, group_collection)

    def visitSourceCollection(self, source_collection):
        OneViewModelInitializer.visitSourceCollection(self, source_collection)

    def visitCompilerCollection(self, compilerCollection):
        pass
