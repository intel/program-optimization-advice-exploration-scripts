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
from abc import ABC, abstractmethod
from util import *
import os
import pandas as pd
from model import *
from model_collection import *
import csv
import time
import pickle
# qaas_database = QaaSDatabase()
# qaas_database.accept(ov_initilizer)

class ModelAccessor(ABC):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def visitQaaSDataBase(self, qaas_database):
        pass
    @abstractmethod
    def visitApplication(self, application):
        pass
    @abstractmethod
    def visitExecution(self, execution):
        pass
    @abstractmethod
    def visitEnvironment(self, environment):
        pass
    @abstractmethod
    def visitOs(self, os):
        pass
    @abstractmethod
    def visitHwSystem(self, hwsystem):
        pass
    @abstractmethod
    def visitMaqao(self, maqao):
        pass
    @abstractmethod
    def visitCompilerCollection(self, compiler_collection):
        pass
    @abstractmethod
    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        pass
    @abstractmethod
    def visitModuleCollection(self, module_collection):
        pass
    @abstractmethod
    def visitBlockCollection(self, block_collection):
        pass
    @abstractmethod
    def visitFunctionCollection(self, function_collection):
        pass
    @abstractmethod
    def visitLoopCollection(self, loop_collection):
        pass
    @abstractmethod
    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        pass
    @abstractmethod
    def visitCqaCollection(self, cqa_collection):
        pass
    @abstractmethod
    def visitAsmCollection(self, asm_collection):
        pass
    @abstractmethod
    def visitGroupCollection(self, group_collection):
        pass
    @abstractmethod
    def visitSourceCollection(self, source_collection):
        pass

class LoreModelAccessor(ModelAccessor):
    def __init__(self, session):
        super().__init__(session)

# For populating OV DB from LORE csv dumps
class LoreMigrator(LoreModelAccessor):
    def __init__(self, session, lore_csv_dir):
        super().__init__(session)
        self.lore_csv_dir = lore_csv_dir

    def find_application_by_id(self, id):
        return self.id_application_obj_dict.get(id, None)
    def find_mutation_by_loop_id_and_mutation_number(self, lookup_key):
        return self.orig_loop_id_mutation_dict.get(lookup_key, None)
    
    def set_application_values(self, workload_name, workload_version_name, workload_program_name,workload_program_commit_id):
        self.workload = workload_name
        self.workload_version = workload_version_name
        self.program = workload_program_name
        self.commit_id = workload_program_commit_id

    def read_executions_in_batch(self, start_row, size):
            with open(os.path.join(self.lore_csv_dir, 'executions.csv'), 'r') as file:
                csv_reader = csv.DictReader(file, delimiter=',')
                for i, row in enumerate(csv_reader):
                    if i < start_row:
                        continue
                    if i >= start_row + size:
                        break
                    self.current_execution_data = row
                    current_execution = Execution(self)
                    if i % 10000 == 0:
                        print(f"Processed {i} rows")

    def visitQaaSDataBase(self, qaas_database):
        start_time = time.time()

        # Application table
        application_df = read_file(os.path.join(self.lore_csv_dir, 'applications.csv'), delimiter=',')
        benchmark_df = read_file(os.path.join(self.lore_csv_dir, 'benchmarks.csv'), delimiter=',')
        benchmark_df.rename(columns={'table_ptr': 'id'}, inplace=True)

        merged_application_df = merge_df(application_df, benchmark_df,  ['benchmark','version'], ['id'])
        application_data = merged_application_df.to_dict(orient='records')
        #used to save the table ptr and application table obj pair
        id_application_obj_dict = {}
        for data_dict in application_data:
            
            benchmark = None if pd.isna(data_dict['benchmark']) else data_dict['benchmark']
            version = None if pd.isna(data_dict['version']) else data_dict['version']
            application = None if pd.isna(data_dict['application']) else data_dict['application']
            table_id = data_dict['table_ptr']
            commit_id = 'commit id' 
            self.set_application_values( benchmark, version, application, commit_id)
            current_application = Application.get_or_create_application(benchmark, version, application, commit_id, self)
            id_application_obj_dict[table_id] = current_application
            qaas_database.add_to_data_list(current_application)
        self.id_application_obj_dict = id_application_obj_dict
        

        #loop collection
        loop_collection = LoopCollection()
        loop_collection.accept(self)

        #hwsystem and os  info
        hw_data = read_file(os.path.join(self.lore_csv_dir, 'hwsystems.csv'), delimiter=',').to_dict(orient='records')[0]
        self.current_hw = HwSystem.get_or_create_hwsystem_by_hw_info(hw_data['name'], hw_data['cpu'], hw_data['memory'], self)
        self.current_os = Os.get_or_create_os_by_os_info(hw_data['os'], self)

        #compiler info
        compiler_collection = CompilerCollection()
        compiler_collection.accept(self)

        #save loop data in memeory
        self.loop_data_df = read_file(os.path.join(self.lore_csv_dir, 'loops.csv'), delimiter=',')


        # execution data
        unneeded_columns_execution = ['id','benchmark', 'version', 'function', 'file', 'line', 'unrolling_arg', 'unrolling_order', 
                                    'unrolljam_order', 'unrolljam_arg', 'tiling_arg','tiling_arg','interchange_arg',
                                    'interchange_arg','mutation_number','distribution_arg','distribution_order','compiler_vendor',
                                    'compiler_version','cpu_model']
        repeapted_orig_data = ['orig_avx_max', 'orig_avx2_max', 'orig_base_max', 'orig_novec_max', 'orig_o3_max', 'orig_sse_max',
                    'orig_avx_mean', 'orig_avx2_mean', 'orig_base_mean', 'orig_novec_mean', 'orig_o3_mean', 'orig_sse_mean',
                    'orig_avx_median', 'orig_avx2_median', 'orig_base_median', 'orig_novec_median', 'orig_o3_median', 'orig_sse_median',
                    'orig_avx_min', 'orig_avx2_min', 'orig_base_min', 'orig_novec_min', 'orig_o3_min', 'orig_sse_min',
                    'orig_avx_sd', 'orig_avx2_sd', 'orig_base_sd', 'orig_novec_sd', 'orig_o3_sd', 'orig_sse_sd']
        unneeded_columns_execution.extend(repeapted_orig_data)
        self.unneeded_columns_execution = unneeded_columns_execution
        self.unneeded_columns_loop = ['id', 'benchmark', 'version', 'application', 'file', 'function', 'line', 'n_executions','table_ptr','n_mutations']
        self.lore_data_path = '/host/home/yjiao/loop_collections_12072018'
        #used to check what is orig loop
        self.orig_src_loop_map = {}
        #iterate all the executions 
        # with open(os.path.join(self.lore_csv_dir, 'executions.csv'), 'r') as file:
        #     csv_reader = csv.DictReader(file, delimiter=',')
        #     for i, row in enumerate(csv_reader):
        #         # if i == 1000:
        #         #     break
        #         #create execution obj for each execution
        #         self.current_execution_data = row
        #         current_execution = Execution(self)
        #         if i % 1000 == 0:
        #             print(i)

        # end_time = time.time()

        # total_execution_time = end_time - start_time
        # print(f"The program took {total_execution_time} seconds to run.")


    def visitApplication(self, application):
        
        application.workload = self.workload
        application.version = self.workload_version
        application.program = self.program
        application.commit_id = self.commit_id

    def visitCompilerCollection(self, compiler_collection):
        compiler_data = read_file(os.path.join(self.lore_csv_dir, 'compilers.csv'), delimiter=',').to_dict(orient='records')
        for dict_data in compiler_data:
            dict_data = delete_nan_from_dict(dict_data)

            Compiler.get_or_create_compiler_by_compiler_info(dict_data.get('vendor', None),
                                                            dict_data.get('version', None),
                                                            self,
                                                            dict_data.get('release_date', None),
                                                            dict_data.get('base_flags', None),
                                                            dict_data.get('novec_flags', None),
                                                            dict_data.get('sse_flags', None),
                                                            dict_data.get('avx_flags', None),
                                                            dict_data.get('avx2_flags', None))


    def visitExecution(self, current_execution):
        #for one execution
        row = self.current_execution_data
        orig_loop_id = row['id']
        file = row['file']
        mutation_number = int(row['mutation_number'])
        #skip pluto run
        if mutation_number == -1:
            return
        lookup_key = f'{orig_loop_id}_{mutation_number}'

        #get application info from orig loop data dict
        orig_src_loop_dict = self.loop_data_df.loc[self.loop_data_df['table_ptr'] == orig_loop_id].to_dict(orient='records')[0]
        assert orig_src_loop_dict is not None, "Using id to get orig src loop, retrieved values is None"
        orig_filename = orig_src_loop_dict['file']
        orig_function_name = orig_src_loop_dict['function']
        orig_line_number = orig_src_loop_dict['line']
        current_application = self.find_application_by_id(orig_src_loop_dict['id'])
        current_execution.application = current_application

        current_execution.hwsystem = self.current_hw
        current_execution.os = self.current_os
        current_execution.universal_timestamp = time.time()

        #create source obj
        source_code_file_name = f'{orig_filename}_{orig_function_name}_line{orig_line_number}_loop.c.{mutation_number}.c'
        source_code_path = os.path.join(self.lore_data_path, current_application.workload, current_application.version, current_application.program, 
                                                    "extractedLoops", f'{get_file_loop_name(source_code_file_name)}_mutations', source_code_file_name)
        #does not have mutation for src loop
        if not os.path.exists(source_code_path):
            # print(source_code_file_name, "does not exist")
            return
        cleaned_data_loop = delete_data_from_dict(orig_src_loop_dict, self.unneeded_columns_loop)
        current_src = Source.get_or_create_source_by_hash(source_code_path, cleaned_data_loop, self)


      

        #create src loop obj for each execution
        #get orig loop if mutation 0 else create a new one for its mutation
        current_src_loop = SrcLoop(self)
        source_code_line_number = get_mutation_line_number(source_code_path)
        current_src_loop.file = source_code_file_name
        current_src_loop.line_number = source_code_line_number

        current_src_loop.source = current_src
        current_src_loop.mutation_number = mutation_number
        current_src_loop.execution = current_execution
        
        #flush to get the id
        self.session.flush()


        #keep track of what orig loop has been created, will use it as fk orign loop for its mutations, fk_orig loop is null
        if mutation_number == 0 and orig_loop_id not in self.orig_src_loop_map:
            self.orig_src_loop_map[orig_loop_id] = current_src_loop.table_id
        #set up foreign key if it is a mutation
        if mutation_number != 0:
            #try to find in map then pickle file, if not foudn in both create new src loop
            found_id = self.orig_src_loop_map.get(orig_loop_id, None)
            if not found_id:
                try:
                    with open('orig_src_loop_map.pkl', 'rb') as f:
                        orig_src_loop_map_from_file = pickle.load(f)
                    found_id = orig_src_loop_map_from_file.get(orig_loop_id, None)
                except (FileNotFoundError, pickle.PickleError):
                    found_id = None


            orig_src_loop = SrcLoop.get_src_loop_by_id(self, found_id)

            #orig loop is not in front of mutation, create empty src loop
            if not orig_src_loop:
                print("create empty src loop")
                orig_src_loop = SrcLoop(self)
                self.orig_src_loop_map[orig_loop_id] = orig_src_loop
            current_src_loop.orig_src_loop = orig_src_loop


        
        #link to mutation
        current_mutation = self.find_mutation_by_loop_id_and_mutation_number(lookup_key)
        assert current_mutation is not None, "Using id + mutation number to get mutation, but retrieved values is None"
        current_src_loop.mutation = current_mutation

        #create and link to loop
        current_loop = Loop(self)
        #link to orig source loop
        current_loop.src_loop = current_src_loop
        
        current_function = Function.get_or_create_function_by_function_name(row['function'], self)
        current_loop.function = current_function
        compiler_vendor = row['compiler_vendor']
        compiler_version = row['compiler_version']
        current_compiler = Compiler.get_compiler_info(compiler_vendor, compiler_version, self)
        current_loop.compiler = current_compiler

        #create the metrics
        current_lore_loop_measure = LoreLoopMeasure(self)
        current_lore_loop_measure.loop = current_loop
        cleaned_data = delete_data_from_dict(row, self.unneeded_columns_execution)
        current_lore_loop_measure.add_metrics(self.session, cleaned_data)


    def visitLoopCollection(self, loop_collection):
        
        #key is id + mutation number value is mutation
        orig_loop_id_mutation_dict = {}
        
                
        with open(os.path.join(self.lore_csv_dir, 'mutations.csv'), 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=',')
            for i, dict_data in enumerate(csv_reader):
                #skip pluto run
                is_pluto = int(dict_data.get('pluto', None))
            
                #get info from dict
                dict_data = delete_nan_from_dict(dict_data)
                mutation_number = int(dict_data.get('mutation_number', None))
                orig_loop_id = dict_data['id']
                if is_pluto == 1 or mutation_number == -1:
                    continue
                #create mutation obj
                current_mutation = Mutation.get_or_create_mutation_by_mutation_info(dict_data, self)
                current_mutation.mutation_number = mutation_number
                current_mutation.pluto = is_pluto
                current_mutation.interchange_order = dict_data.get('interchange_order', None)
                current_mutation.interchange_arg = dict_data.get('interchange_arg', None)
                current_mutation.tiling_order = dict_data.get('tiling_order', None)
                current_mutation.tiling_arg = dict_data.get('tiling_arg', None)
                current_mutation.unrolling_order = dict_data.get('unrolling_order', None)
                current_mutation.unrolling_arg = dict_data.get('unrolling_arg', None)
                current_mutation.distribution_order = dict_data.get('distribution_order', None)
                current_mutation.distribution_arg = dict_data.get('distribution_arg', None)
                current_mutation.unrolljam_order = dict_data.get('unrolljam_order', None)
                current_mutation.unrolljam_arg = dict_data.get('unrolljam_arg', None)
                current_mutation.valid = dict_data.get('valid', None)

                orig_loop_id_mutation_dict[f'{orig_loop_id}_{mutation_number}'] = current_mutation
              
        self.orig_loop_id_mutation_dict = orig_loop_id_mutation_dict     
       

    
    def visitEnvironment(self, environment):
        pass
    def visitOs(self, os):
        pass
    def visitHwSystem(self, hwsystem):
        pass
    def visitMaqao(self, maqao):
        pass
    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        pass
    def visitModuleCollection(self, module_collection):
        pass
    def visitBlockCollection(self, block_collection):
        pass
    def visitFunctionCollection(self, function_collection):
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


