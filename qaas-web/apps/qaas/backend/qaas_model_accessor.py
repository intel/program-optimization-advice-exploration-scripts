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
from qaas_util import parse_text_to_dict
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
    def __init__(self, session, report_path):
        super().__init__(session)
        self.report_path = report_path
        self.qaas_metadata_file_path = os.path.join(report_path, 'input.txt')

        self.current_row = None
        self.current_type = None
            
    def build_executions_from_file(self, file_path, report_type, qaas_database, metadata_dict):
        #read scability report path
        if os.path.exists(file_path):
            df = read_file(file_path, delimiter=',')
            self.current_type = report_type
            #iterate file each row in the file is new execution
            for index, row in df.iterrows():
                self.current_row = row
                current_application = Application(self)
                current_application.mpi_scaling = metadata_dict['mpi_scaling']
                current_application.omp_scaling = metadata_dict['openmp_scaling']
                current_execution = Execution(self)
                ### set the execution 
                self.current_execution = current_execution
                current_execution.application = current_application
                qaas_database.add_to_data_list(current_execution)

                ###os
                current_os = Os(self)
                current_execution.os = current_os
                ###hw system
                current_hwsystem = HwSystem(self)
                current_execution.hwsystem = current_hwsystem
        
    def visitQaaSDataBase(self, qaas_database):
        #get metadata
        metadata_dict = parse_text_to_dict(self.qaas_metadata_file_path)
        #get data files
        if metadata_dict['multicompiler_report']:
            multicompiler_report_file_name = metadata_dict['multicompiler_report']
            multicompiler_report_path = os.path.join(self.report_path, multicompiler_report_file_name)
            self.build_executions_from_file(multicompiler_report_path, 'multicompiler_report', qaas_database, metadata_dict)

        if metadata_dict['scalability_report']:
            scalability_report_file_name = metadata_dict['scalability_report']
            scalability_report_path = os.path.join(self.report_path, scalability_report_file_name)
            #read scability report 
            self.build_executions_from_file(scalability_report_path, 'scalability_report', qaas_database, metadata_dict)

        

             
   
    def visitApplication(self, application):
        metadata_dict = parse_text_to_dict(self.qaas_metadata_file_path)
        application.workload = metadata_dict['app_name']
        
    def visitExecution(self, execution):
        #metadata info
        metadata_dict = parse_text_to_dict(self.qaas_metadata_file_path)

        #create qaas and exectuion assoicate table
        #both multicompiler report and scabilty belong to same qaas 
        timestamp = metadata_dict['timestamp']
        current_qaas = QaaS.get_or_create_qaas(timestamp, self)
        current_qaas_run = QaaSRun(self)
        #associate table
        current_qaas_run.execution = execution
        current_qaas_run.qaas = current_qaas
        current_qaas_run.type = self.current_type

        #data info
        execution.time = self.current_row['time(s)']
        compiler_vendor = self.current_row['compiler']
        compiler_flag = self.current_row.get('flags', None)
        config = {
            'MPI_threads' : self.current_row['#MPI'],
            'OMP_threads' : self.current_row['#OMP'],
            'affinity': self.current_row.get('affinity', None)
        }
        execution.config = config
        global_metrics_dict = {"Gflops": self.current_row['GFlops/s'] if "GFlops/s" in self.current_row else self.current_row['Gflops/s']}
        execution.global_metrics = global_metrics_dict
        #if it is orig we need to replace it with the actual compiler from metadata
        if compiler_vendor == 'orig':
            compiler_vendor = metadata_dict['compiler_default']
            current_qaas.orig_execution = execution

        
        #get compiler version from metadata
        compiler_version = None
        if compiler_vendor == 'icc':
            compiler_version = metadata_dict['icc_version']
        elif compiler_vendor == 'icx':
            compiler_version = metadata_dict['icx_version']
        elif compiler_vendor == 'gcc':
            compiler_version = metadata_dict['gcc_version']
        compiler = Compiler.get_or_create_compiler_by_compiler_info(vendor=compiler_vendor, version=compiler_version, initializer=self)
        
        compiler_option = CompilerOption(self)
        compiler_option.flag = compiler_flag
        #have to create one compielr option per execution otherwise will overwrite the compiler for the flag
        # compiler_option = CompilerOption.get_or_create_compiler_option(compiler_flag, self)
        #this will overwrite the compiler for the flag
        compiler_option.compiler = compiler
        execution.compiler_option = compiler_option


      


    def visitQaaS(self, qaas):
        pass
    def visitEnvironment(self, environment):
        pass
    def visitOs(self, os):
        metadata_dict = parse_text_to_dict(self.qaas_metadata_file_path)
        os.driver_frequency = metadata_dict['frequency_driver']
        os.scaling_governor = metadata_dict['frequency_governor']
        os.huge_pages = metadata_dict['huge_pages']
        os.hostname = metadata_dict['machine']
        os.scaling_max_frequency = metadata_dict['scaling_max_frequency']
        os.scaling_min_frequency = metadata_dict['scaling_min_frequency']
      
    def visitHwSystem(self, hwsystem):
        metadata_dict = parse_text_to_dict(self.qaas_metadata_file_path)
        hwsystem.cpui_model_name = metadata_dict['model_name']
        hwsystem.cpui_cpu_cores = metadata_dict['number_of_cores']
        hwsystem.sockets = metadata_dict['number_of_sockets']
        hwsystem.cores_per_socket = metadata_dict['number_of_cores_per_socket']
        hwsystem.architecture = metadata_dict['architecture']
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


