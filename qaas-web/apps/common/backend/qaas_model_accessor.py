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
from model_collection import *
from base_util import *
import configparser

class QaaSModelInitializer(ModelAccessor):
    def __init__(self, session, report_path):
        super().__init__(session)
        self.report_path = report_path
        self.qaas_metadata_file_path = os.path.join(report_path, 'input.txt')

        self.current_row = None
        self.current_type = None
        self.current_metadata_config = None

    #set is_baseline based on input scalability_reference_line
    def set_is_baseline(self, df, scalability_reference_line):
        df['is_baseline'] = 0

        #if we don't have a baseline def then it is all false
        if not scalability_reference_line:
            return df
        
        #setting baseline = true if found in ref line
        baseline_indices = {}
        for item in scalability_reference_line.split(','):
            compiler, line = item.strip().replace('"', '').split(':')
            baseline_indices[compiler.strip()] = int(line)

        for compiler, baseline_index in baseline_indices.items():
            pandas_index = baseline_index - 2
            df.loc[(df['compiler'] == compiler) & (df.index == pandas_index), 'is_baseline'] = 1

        return df
    
    def build_executions_from_file(self, file_path, report_type, qaas_database):
        #read scability report path
        if os.path.exists(file_path):
            df = read_file(file_path, delimiter=',')

            #set is_basleine
            scalability_reference_line = self.current_metadata_config['SYSTEM'].get('scalability_reference_line')
            self.set_is_baseline(df, scalability_reference_line)

            #set type
            self.current_type = report_type
            #iterate file each row in the file is new execution
            for index, row in df.iterrows():
                self.current_row = row
                self.set_qaas_row_metrics(qaas_database)

    def set_qaas_row_metrics(self, qaas_database):
        current_application = Application(self)
        current_application.mpi_scaling = self.current_metadata_config['SYSTEM'].get('mpi_scaling')
        current_application.omp_scaling = self.current_metadata_config['SYSTEM'].get('openmp_scaling')
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
        self.current_metadata_config = get_config_from_path(self.qaas_metadata_file_path)
        #check existing qaas
        timestamp = self.current_metadata_config['QAAS'].get('timestamp')        
        if QaaS.qaas_exist(timestamp, self): 
            print("QaaS data already exists, skip database population")
            return
        #get data files
        if self.current_metadata_config['REPORTS'].get('multicompiler_report'):
            multicompiler_report_file_name = self.current_metadata_config['REPORTS'].get('multicompiler_report')
            multicompiler_report_path = os.path.join(self.report_path, multicompiler_report_file_name)
            self.build_executions_from_file(multicompiler_report_path, 'multicompiler_report', qaas_database)

        if self.current_metadata_config['REPORTS'].get('scalability_report'):
            scalability_report_file_name = self.current_metadata_config['REPORTS'].get('scalability_report')
            scalability_report_path = os.path.join(self.report_path, scalability_report_file_name)
            #read scability report 
            self.build_executions_from_file(scalability_report_path, 'scalability_report', qaas_database)

        

             
   
    def visitApplication(self, application):
        application.workload = self.current_metadata_config['QAAS'].get('app_name')
        
    def visitExecution(self, execution):
        #metadata info
        #create qaas and exectuion assoicate table
        #both multicompiler report and scabilty belong to same qaas 
        timestamp = self.current_metadata_config['QAAS'].get('timestamp')        
        current_qaas = QaaS.get_or_create_qaas(timestamp, self)
        current_qaas_run = QaaSRun(self)
        #associate table
        current_qaas_run.execution = execution
        current_qaas_run.qaas = current_qaas
        current_qaas_run.type = self.current_type
        current_qaas_run.is_baseline = self.current_row['is_baseline']


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
            compiler_vendor = self.current_metadata_config['REPORTS'].get('compiler_default')
            current_qaas.orig_execution = execution

        
        #get compiler version from metadata
        compiler_version = None
        if compiler_vendor == 'icc':
            compiler_version = self.current_metadata_config['SYSTEM'].get('icc_version')
        elif compiler_vendor == 'icx':
            compiler_version = self.current_metadata_config['SYSTEM'].get('icx_version')
        elif compiler_vendor == 'gcc':
            compiler_version = self.current_metadata_config['SYSTEM'].get('gcc_version')
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
        os.driver_frequency = self.current_metadata_config['SYSTEM'].get('frequency_driver')
        os.scaling_governor = self.current_metadata_config['SYSTEM'].get('frequency_governor')
        os.huge_pages = self.current_metadata_config['SYSTEM'].get('huge_pages')
        os.hostname = self.current_metadata_config['SYSTEM'].get('machine')
       
    def visitHwSystem(self, hwsystem):
        #need to get or set cannot create in hwsystem
        hwsystem = HwSystem.get_or_set_hwsystem(self.current_metadata_config['SYSTEM'].get('model_name'), self.current_metadata_config['SYSTEM'].get('ISA'), self.current_metadata_config['SYSTEM'].get('architecture'), hwsystem, self)
        hwsystem.cpui_cpu_cores = self.current_metadata_config['SYSTEM'].get('number_of_cores')
        hwsystem.sockets = self.current_metadata_config['SYSTEM'].get('number_of_sockets')
        hwsystem.cores_per_socket = self.current_metadata_config['SYSTEM'].get('number_of_cores_per_socket')
        hwsystem.max_frequency = self.current_metadata_config['SYSTEM'].get('scaling_max_frequency')
        hwsystem.min_frequency = self.current_metadata_config['SYSTEM'].get('scaling_min_frequency')
      
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


