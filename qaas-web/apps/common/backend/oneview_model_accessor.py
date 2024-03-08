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
import shutil
from model_accessor_base import ModelAccessor
from model import *
from model_collection import *
from base_util import *


class OneviewModelAccessor(ModelAccessor):
    def __init__(self, session, qaas_data_dir=None):
        super().__init__(session)
        if qaas_data_dir: self.set_ov_path(qaas_data_dir)
        self.vprof_bucket_range = ["0.00-2.00", "2.00-4.00", "4.00-8.00", "8.00-16.00", "16.00-32.00", "32.00-64.00", "64.00-128.00", "128.00-256.00", "256.00-512.00", "512.00-1024.00", "1024.00-2048.00", "2048.00+"]


    def set_ov_path(self, qaas_data_dir):
        self.qaas_data_dir = qaas_data_dir
        self.cur_run_id = 0
        self.static_dir_path = os.path.join(self.qaas_data_dir, "static_data")
        self.run_dir_path = os.path.join(self.qaas_data_dir, "shared", self.get_run_name())

        self.log_dir = os.path.join(self.qaas_data_dir, 'logs')
        self.source_dir = os.path.join(self.static_dir_path, "sources")
        self.lprof_dir_path = os.path.join(self.qaas_data_dir, "shared",f"lprof_npsu_{self.get_run_name()}")
        self.hierarchy_dir_path = os.path.join(self.static_dir_path, 'hierarchy')
        self.callchain_dir_path = os.path.join(self.lprof_dir_path, 'callchains')

        self.local_vars_path = os.path.join(self.run_dir_path, 'local_vars.csv')
        self.expert_loop_path = os.path.join(self.run_dir_path, "expert_loops.csv")



    def get_run_name(self):
        return f"run_{self.cur_run_id}"
    
    def get_env_path(self):
        self.run_dir_path = os.path.join(self.qaas_data_dir, "shared",self.get_run_name())
        os.makedirs(self.run_dir_path, exist_ok=True)

        return self.run_dir_path
    def get_execution_path(self):
        # Directory paths

        # File paths
        # local_vars_path = os.path.join(self.static_dir_path, 'local_vars.csv')
        config_path = os.path.join(self.run_dir_path, 'config.lua')
        config_out_path = os.path.join(self.run_dir_path, 'config.lua')
        cqa_context_path = os.path.join(self.static_dir_path, "cqa", "cqa_context.lua")
        expert_run_path = os.path.join(self.run_dir_path, 'expert_run.csv')
        #log files
        log_path = os.path.join(self.log_dir, 'log.txt')
        lprof_log_path = os.path.join(self.log_dir, self.get_run_name(), 'lprof.log')
        #location binaries
        fct_locations_path = os.path.join(self.source_dir, 'fct_locations.bin')
        loop_locations_path = os.path.join(self.source_dir, 'loop_locations.bin')

        ##callchain binary
        fct_callchain_path = os.path.join(self.callchain_dir_path, 'cc_fcts.cc')
        loop_callchain_path = os.path.join(self.callchain_dir_path, 'cc_loops.cc')
        #global_metrics csv and compilation options lua
        global_metrics_path = os.path.join(self.run_dir_path, 'global_metrics.csv')
        compilation_options_path = os.path.join(self.source_dir, 'compilation_options.csv')

        return  self.local_vars_path, config_path, config_out_path, cqa_context_path, expert_run_path, log_path,lprof_log_path,\
                fct_locations_path,loop_locations_path, global_metrics_path, compilation_options_path, fct_callchain_path, loop_callchain_path
    
    def get_os_path(self):
        return  self.local_vars_path

    def get_hwsystem_path(self):
        return self.local_vars_path

    
    def get_maqao_path(self):
        return  self.local_vars_path
    
    def get_decan_path(self):
        return os.path.join(self.run_dir_path, "decan.csv")
    
    def get_vprof_path(self):
        return os.path.join(self.run_dir_path, "vprof.csv")
    def get_lprof_categorization_path(self):
        lprof_categorization_path1 = os.path.join(self.run_dir_path, 'lprof_categorization.csv')
        lprof_categorization_path2 = os.path.join(self.lprof_dir_path, 'lprof_categorization.csv')

        return lprof_categorization_path1, lprof_categorization_path2

    def get_function_path(self):
        return self.lprof_dir_path

    def get_module_path(self):
        lprof_path = os.path.join(self.lprof_dir_path,'lprof_modules.csv')
        return lprof_path
    def get_block_path(self):
        return self.lprof_dir_path
    def get_loop_path(self):
        return self.lprof_dir_path, self.hierarchy_dir_path
    
    def get_lprof_measurement_path(self):
        return self.lprof_dir_path, self.expert_loop_path,self.hierarchy_dir_path
    def get_cqa_path(self):
        cqa_dir_path = os.path.join(self.static_dir_path, "cqa")
        return cqa_dir_path, self.expert_loop_path
    def get_asm_path(self):
        asm_dir_path = os.path.join(self.static_dir_path, "asm")
        asm_mapping_dir = os.path.join(self.qaas_data_dir, "tools", "decan", self.get_run_name(), "others")
        return asm_dir_path, asm_mapping_dir
    def get_group_path(self):
        group_dir_path = os.path.join(self.static_dir_path, "groups")
        return group_dir_path
    def get_source_path(self):
        source_dir_path = os.path.join(self.static_dir_path, "sources")
        return source_dir_path

   
   

class OneViewModelInitializer(OneviewModelAccessor):
    def __init__(self, session, qaas_data_dir=None, qaas_timestamp=None, version=None, workload_name=None, workload_version_name=None, workload_program_name=None, workload_program_commit_id=None):
        super().__init__(session, qaas_data_dir)
        #execution
        self.qaas_timestamp = qaas_timestamp
        self.version = version
        #application
        self.workload = workload_name
        self.workload_version = workload_version_name
        self.program = workload_program_name
        self.commit_id = workload_program_commit_id

    def get_current_execution(self):
        return self.current_execution
    

    def set_ov_row_metrics(self, current_execution, qaas_database, current_os):
        # # ###maqao table
        current_maqao = Maqao(self)
        current_maqao.execution = current_execution
        qaas_database.add_to_data_list(current_maqao)

        ###### environment, environment metrics
        current_environment = Environment( self)
        current_os.environment = current_environment
        qaas_database.add_to_data_list(current_environment)

  

        #########lprof categorization table and lprof categorization metrics
        current_lprof_categorization_collection = LprofCategorizationCollection()
        current_lprof_categorization_collection.accept(self)
        current_execution.lprof_categorizations = current_lprof_categorization_collection.get_objs()
        qaas_database.add_to_data_list(current_lprof_categorization_collection)

        # ####lprofs_module.csv
        module_collection = ModuleCollection()
        module_collection.accept(self)
        current_execution.modules = module_collection.get_objs()
        qaas_database.add_to_data_list(module_collection)

        ####lprof_blocks
        block_collection = BlockCollection()
        block_collection.accept(self)
        current_execution.blocks = block_collection.get_objs()
        qaas_database.add_to_data_list(block_collection)

        ####lprof functiona and loops
        function_collection = FunctionCollection( )
        function_collection.accept(self)

        loop_collection = LoopCollection()
        loop_collection.accept(self)

        qaas_database.add_to_data_list(function_collection)
        qaas_database.add_to_data_list(loop_collection)

        ##### decan collection 
        current_decan_collection = DecanCollection()
        current_decan_collection.accept(self)
        qaas_database.add_to_data_list(current_decan_collection)

      
        ###lprof easure ments
        lprof_measurement_collection = LprofMeasurementCollection(  block_collection, function_collection, loop_collection)
        lprof_measurement_collection.accept(self)

        qaas_database.add_to_data_list(lprof_measurement_collection)

        # ####cqa dir csv
        cqa_collection = CqaCollection()
        cqa_collection.accept(self)
        qaas_database.add_to_data_list(cqa_collection)

        # #####asm dir csv
        asm_collection = AsmCollection()
        asm_collection.accept(self)
        qaas_database.add_to_data_list(asm_collection)

        ####group dir csv
        group_collection = GroupCollection()
        group_collection.accept(self)
        qaas_database.add_to_data_list(group_collection)


        ####source compilation_options.csv
        source_collection = SourceCollection()        
        source_collection.accept(self)
        qaas_database.add_to_data_list(source_collection)

        ##### vprof collection 
        current_vprof_collection = VprofCollection()
        current_vprof_collection.accept(self)
        qaas_database.add_to_data_list(current_vprof_collection)
        
    def visitQaaSDataBase(self, qaas_database):
        print("ov visit qaad db called")
        current_application = Application(self)
        current_execution = Execution(self)
        ### set the execution 
        self.current_execution = current_execution
        qaas_database.universal_timestamp = current_execution.universal_timestamp

        current_execution.application = current_application
        qaas_database.add_to_data_list(current_execution)
        
      
        # ##hwsystem table
        current_hw = HwSystem(self)
        current_execution.hwsystem = current_hw
        qaas_database.add_to_data_list(current_hw)

        # ###os table
        current_os = Os(self)
        current_execution.os = current_os
        qaas_database.add_to_data_list(current_os)

        self.set_ov_row_metrics(current_execution, qaas_database, current_os)


       
        

    def visit_file(self, file):
        return file

    def visitEnvironment(self, environment):
        self.run_dir_path=self.get_env_path()

        env_path = get_files_starting_with_and_ending_with(self.run_dir_path, 'env_','.txt')[0]

        env_data = convert_text_to_dict(self.visit_file(env_path))
        
        #add metric
        env_metrics = environment.add_metrics(self.session, env_data)

    def visitApplication(self, application):
        application.workload = self.workload
        application.version = self.workload_version
        application.program = self.program
        application.commit_id = self.commit_id

    def visitExecution(self, execution):
        execution.qaas_timestamp = self.qaas_timestamp
        execution.version = self.version
        local_vars_path, config_path, config_out_path, cqa_context_path, expert_run_path, log_path,lprof_log_path,\
            fct_locations_path,loop_locations_path, global_metrics_path, compilation_options_path, fct_callchain_path, loop_callchain_path = self.get_execution_path()
        local_vars_df = read_file(self.visit_file(local_vars_path))
        local_vars_dict = local_vars_df.set_index('metric')['value'].to_dict()


        execution.is_src_code = local_vars_dict.get('is_src_code', 'false').lower() == 'true'
        execution.universal_timestamp = local_vars_dict.get('universal_timestamp', None)

        #add additional cols
        execution.is_orig = 1 if execution.version == 'orig' else 0

        #make sure config is a dic
        if execution.config is None:
            execution.config = {}
        # #config lua and cqa_context
        additonal_config = convert_lua_to_python(config_path)
        if additonal_config:
        #in case qaas already has some configurations appenbd it
            execution.config = {**execution.config, **additonal_config}

        execution.cqa_context = convert_lua_to_python(self.visit_file(cqa_context_path))
        
        # #get time, profiled time, and max_nb_threads from expert loops
        expert_run_data = get_data_from_csv(self.visit_file(expert_run_path))[0]
        execution.time = expert_run_data.get('time', None)
        execution.profiled_time = expert_run_data.get('profiled_time', None)
        execution.max_nb_threads = expert_run_data.get('max_nb_threads', None)

        # #get log files
        execution.log = compress_file(self.visit_file(log_path))
        execution.lprof_log = compress_file(self.visit_file(lprof_log_path))

        # #get src location for fct and loop
        # #get the location binary files
        source_loop_python_obj = convert_location_binary_to_python(self.visit_file(loop_locations_path), self.session)
        source_fct_python_obj = convert_location_binary_to_python(self.visit_file(fct_locations_path), self.session)
        execution.fct_location = source_fct_python_obj
        execution.loop_location = source_loop_python_obj

        ##callchain binary
        callchain_fct_python_obj = convert_callchain_binary_to_python(self.visit_file(fct_callchain_path), self.session)
        callchain_loop_python_obj = convert_callchain_binary_to_python(self.visit_file(loop_callchain_path), self.session)
        execution.fct_callchain = callchain_fct_python_obj
        execution.loop_callchain = callchain_loop_python_obj
        ##global metrics
        global_metrics_df = read_file(self.visit_file(global_metrics_path))
        compilation_options_df = read_file(self.visit_file(compilation_options_path))

        # make sure execution.global_metrics is initialized as a dictionary if it is None
        if execution.global_metrics is None:
            execution.global_metrics = {}
        global_metrics_dict={
            'global_metrics': global_metrics_df.to_json(orient="split"),
            'compilation_options': compilation_options_df.to_json(orient="split")
        }
        #in case qaas already has some configurations
        execution.global_metrics = {**execution.global_metrics, **global_metrics_dict}
        execution.threads_per_core = local_vars_dict.get('threads_per_core', None)


    def visitOs(self, os):
        local_vars_path=self.get_os_path()
        local_vars_df = read_file(self.visit_file(local_vars_path))
        local_vars_dict = local_vars_df.set_index('metric')['value'].to_dict()
        os.os_version = local_vars_dict.get('os_version', None)
        os.hostname = local_vars_dict.get('hostname', None)
        os.huge_pages = local_vars_dict.get('huge_pages', None)
        os.driver_frequency = local_vars_dict.get('driver_frequency', None)

    def visitHwSystem(self, hwsystem):
        local_vars_path = self.get_hwsystem_path()
        local_vars_df = read_file(self.visit_file(local_vars_path))
        local_vars_dict = local_vars_df.set_index('metric')['value'].to_dict()
        hwsystem.cpui_model_name =  local_vars_dict.get('cpui_model_name', None)
        hwsystem.cpui_cpu_cores = local_vars_dict.get('cpui_cpu_cores', None)
        hwsystem.cpui_cache_size =  local_vars_dict.get('cpui_cache_size', None)
        hwsystem.cur_frequency =  local_vars_dict.get('cur_frequency', None)
        hwsystem.max_frequency = local_vars_dict.get('max_frequency', None)
        hwsystem.architecture =  local_vars_dict.get('architecture', None)
        hwsystem.uarchitecture =  local_vars_dict.get('uarchitecture', None)
        hwsystem.proc_name =  local_vars_dict.get('proc_name', None)
        hwsystem.sockets =  local_vars_dict.get('sockets', None)
        hwsystem.cores_per_socket =  local_vars_dict.get('cores_per_socket', None)


    def visitMaqao(self, maqao):
        local_vars_path=self.get_maqao_path()
        local_vars_df = read_file(self.visit_file(local_vars_path))
        local_vars_dict = local_vars_df.set_index('metric')['value'].to_dict()
        maqao.global_instances_per_bucket = local_vars_dict.get('global_instances_per_bucket', None)
        maqao.instances_per_bucket = local_vars_dict.get('instances_per_bucket', None)
        maqao.architecture_code = local_vars_dict.get('architecture_code', None)
        maqao.uarchitecture_code = local_vars_dict.get('uarchitecture_code', None)
        maqao.min_time_obj = local_vars_dict.get('min_time_obj', None)
        maqao.cqa_uarch = local_vars_dict.get('cqa_uarch', None)
        maqao.cqa_arch = local_vars_dict.get('cqa_arch', None)
        maqao.lprof_suffix = local_vars_dict.get('lprof_suffix', None)
        maqao.last_html_path = local_vars_dict.get('last_html_path', None)
        maqao.maqao_build = local_vars_dict.get('maqao_build', None)
        maqao.maqao_version = local_vars_dict.get('maqao_version', None)
        maqao.exp_version = local_vars_dict.get('exp_version', None)
        maqao.nb_filtered_functions = local_vars_dict.get('nb_filtered_functions', None)
        maqao.cov_filtered_loops = local_vars_dict.get('cov_filtered_loops', None)
        maqao.nb_filtered_loops = local_vars_dict.get('nb_filtered_loops', None)
        maqao.config_count = local_vars_dict.get('config_count', None)
        maqao.cov_filtered_functions = local_vars_dict.get('cov_filtered_functions', None)

    def visitDecanCollection(self, decan_collection):
        decan_path = self.get_decan_path()
        if not os.path.exists(decan_path):
            return
        decan_data = read_file(self.visit_file(decan_path)).to_dict(orient='records')
        for dic in decan_data:
            current_decan = DecanRun(self)
            current_decan.bucket = int(dic.get('bucket', None))
            current_decan.frequency = float(dic.get('frequency', None))
            current_decan.type = dic.get('type', None)
            current_decan.mpi_process = dic.get('mpi_process', None)
            current_decan.thread = dic.get('thread', None)
            module = dic.get('module', None)

            current_decan.add_metric(self, dic.get('metric', None), float(dic.get('value', 0.0)), dic.get('value_type', None))

            
            current_loop = get_loop_by_maqao_id_module(self.get_current_execution(), int(dic.get('id', None)), module)
            current_decan.loop = current_loop
            current_variant = DecanVariant.get_or_create_by_name(dic.get('variant', None), self)
            current_decan.decan_variant = current_variant 
            decan_collection.add_obj(current_decan)


    def visitVprofCollection(self, vprof_collection):
        vprof_path = self.get_vprof_path()
        if not os.path.exists(vprof_path):
            return

        vprof_data = read_file(self.visit_file(vprof_path), delimiter=',')
        vprof_data = vprof_data.to_dict(orient='records')

        for dic in vprof_data:
            dic = delete_nan_from_dict(dic)
            current_vprof = VprofMeasure(self)
            
            current_vprof.instance_count = dic.get('instance_count', None) 
            current_vprof.invalid_count = dic.get('invalid_count', None)  
            current_vprof.iteration_total = dic.get('iteration_total', None) 
            current_vprof.iteration_min = dic.get('iteration_min', None) 
            current_vprof.iteration_max = dic.get('iteration_max', None) 
            current_vprof.iteration_mean = dic.get('iteration_mean', None)  
            current_vprof.cycle_total = dic.get('cycle_total', None) 
            current_vprof.cycle_min = dic.get('cycle_min', None) 
            current_vprof.cycle_max = dic.get('cycle_max', None) 
            current_vprof.cycle_mean = dic.get('cycle_mean', None) 
            current_vprof.cycles_per_iteration_min = dic.get('cycles_per_iteration_min', None) 
            current_vprof.cycles_per_iteration_max = dic.get('cycles_per_iteration_max', None) 
            current_vprof.cycles_per_iteration_mean = dic.get('cycles_per_iteration_mean', None)  

            #use only id because it is using binary as a place holder not a real module name
            current_loop = get_loop_by_maqao_id(self.get_current_execution(),  dic.get('loop_id', None))

            current_vprof.loop = current_loop

            for bucket_range in self.vprof_bucket_range:
                bucket_measure = VprofBucketMeasure(self)
                bucket_measure.range_value = bucket_range
                bucket_measure.bucket_instance_percent = dic.get('bucket_instance_percent_' + bucket_range, None)
                bucket_measure.bucket_cycle_percent = dic.get('bucket_cycle_percent_' + bucket_range, None)
                bucket_measure.bucket_instances = dic.get('bucket_instances_' + bucket_range, None)

                current_vprof.vprof_bucket_measures.append(bucket_measure)
                
            vprof_collection.add_obj(current_vprof)
    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        lprof_categorization_path1, lprof_categorization_path2 = self.get_lprof_categorization_path()
        lprof_categorization_csv_df = read_file(self.visit_file(lprof_categorization_path1))
        lprof_categorization_metrics_data = lprof_categorization_csv_df.loc[:, lprof_categorization_csv_df.columns.str.contains('%')].to_dict(orient='records')
        lprof_categorization_data = get_table_data_from_df(lprof_categorization_csv_df, LprofCategorization)
        for index, parent_dict in enumerate(lprof_categorization_data):
            parent_obj = LprofCategorization(self)
            parent_obj.node = parent_dict['Node']
            parent_obj.process=parent_dict['Process']
            parent_obj.thread=parent_dict['Thread']
            parent_obj.nb_cycle_events=parent_dict['Nb Cycle Events']
            parent_obj.time_s=parent_dict['Time (s)']

            #add metric
            metrics =   parent_obj.add_metrics(self.session, lprof_categorization_metrics_data[index])
            lprof_categorization_collection.add_obj(parent_obj)

    
    def visitModuleCollection(self, module_collection):
        lprof_path = self.get_module_path()
        lprof_df = read_file(self.visit_file(lprof_path))
        module_data_list = get_table_data_from_df(lprof_df, Module)
        for data in module_data_list:
            data = delete_nan_from_dict(data)
            module = Module.get_or_create_by_name(data.get('name', None), self.get_current_execution(), self)
            module.time_p = data.get('time_p',None)
            module.time_s = data.get('time_s',None)
            module.cpi_ratio = data.get('cpi_ratio', None)
            module_collection.add_obj(module)

    def visitBlockCollection(self, block_collection):
        lprof_dir_path = self.get_block_path()
        lprof_pattern = r'lprof_blocks_([\w\.]+)_(\d+)_(\d+).csv'
        #pid and tid null means overall measurement
        files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_blocks', '.csv')
        for file in files:
            #check if there is pid and tid in the file name
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
                
            data = read_file(self.visit_file(file)).to_dict(orient='records')
            #empty file
            if not data:
                current_block = Block(self)
                current_block.pid = pid
                current_block.tid = tid 
                block_collection.add_obj(current_block)
            else:
                for d_dict in data:
                    module_name = d_dict['module']
                    current_module = get_module_by_name(self.get_current_execution().modules, module_name)
                    source_name, line_number = parse_source_info(d_dict['source_info'])
                    current_block = Block(self)
                    current_block.maqao_block_id = d_dict['block_id']
                    current_block.file=source_name
                    current_block.line_number=line_number
                    current_block.pid = pid
                    current_block.tid = tid 
                    current_block.module =  current_module  
                    block_collection.add_obj(current_block)



    def visitFunctionCollection(self, function_collection):
        lprof_dir_path = self.get_function_path()
        lprof_pattern = r'lprof_functions_([\w\.]+)_(\d+)_(\d+).csv'
        files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_functions', '.csv')
        for file in files:
            data = read_file(self.visit_file(file)).to_dict(orient='records')
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
            
            #empty file
            if not data:
                current_function = Function(self)
                current_function.pid = pid
                current_function.tid = tid 
                function_collection.add_obj(current_function)
            else:
                for d_dict in data:
                    #src_function
                    src_function = None

                    src_function = SrcFunction(self)
                    src_function.execution = self.get_current_execution()

                    if not is_nan(d_dict['source_info']): 
                        source_file, line_number = parse_source_info(d_dict['source_info'])
                        src_function.file = source_file
                        src_function.line_number = line_number

                    #function
                    module_name = d_dict['module']
                    current_module = get_module_by_name(self.get_current_execution().modules, module_name)
                    current_function = Function(self)
                    current_function.function_name = d_dict['function_name']
                    current_function.label_name=d_dict['label_name']
                    current_function.maqao_function_id = int(d_dict['function_id'])
                    current_function.cats = d_dict['cats']
                    current_function.pid = pid
                    current_function.tid = tid 
                    current_function.module =  current_module  
                    current_function.src_function = src_function
                    function_collection.add_obj(current_function)

    def visitLoopCollection(self, loop_collection):
        lprof_dir_path, hierarchy_dir_path = self.get_loop_path()
        lprof_pattern = r'lprof_loops_([\w\.]+)_(\d+)_(\d+).csv'
        files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_loops', '.csv')
        for file in files:
            data = read_file(self.visit_file(file)).to_dict(orient='records')
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
            #empty file
            if not data:
                current_loop = Loop(self)
                current_loop.pid = pid
                current_loop.tid = tid 
                loop_collection.add_obj(current_loop)
            for d_dict in data:
                #src_loop
                src_loop = None

                src_loop = SrcLoop(self)
                src_loop.execution = self.get_current_execution()

                if not is_nan(d_dict['source_info']): 
                    source_file, line_number = parse_source_info(d_dict['source_info'])
                    src_loop.file = source_file
                    src_loop.line_number = line_number

                #loop
                d_dict['level'] = reverse_level_map[d_dict['level']]
                current_loop = Loop(self)
                current_loop.maqao_loop_id = d_dict['loop_id']
                current_loop.level = d_dict['level']
                
                current_loop.pid = pid
                current_loop.tid = tid 

                maqao_function_id = d_dict['function_id']
                module = d_dict['module']
                current_function = get_function_by_maqao_id_module(self.get_current_execution(), maqao_function_id, module)  
                current_loop.src_loop = src_loop
                current_loop.function = current_function
                loop_collection.add_obj(current_loop)

        #create cqa hierarch column
        loop_functions = get_all_functions(loop_collection)
        for function in loop_functions:
            if function:
                hierarchy_file_name = 'fct_{}_{}.lua'.format(os.path.basename(function.module.name), function.maqao_function_id)
                hierarchy_file_path = os.path.join(hierarchy_dir_path,hierarchy_file_name)
                hierarchy_json_data = convert_lua_to_python(self.visit_file(hierarchy_file_path))
                function.hierarchy = hierarchy_json_data


        
    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        lprof_dir_path, expert_loop_path, hierarchy_dir_path = self.get_lprof_measurement_path()
        block_files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_blocks', '.csv')
        function_files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_functions', '.csv')
        loop_files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_loops', '.csv')
        #TODO read pid tid file and lprof_blocks.cs separately
        for file in block_files:
            lprof_pattern = r'lprof_blocks_([\w\.]+)_(\d+)_(\d+).csv'
            data = read_file(self.visit_file(file)).to_dict(orient='records')
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
            #empty file
            if not data:
                current_block = get_block(lprof_measurement_collection.block_collection.get_objs(), None, pid, tid) 
                measure = LprofMeasurement(self)
                measure.block = current_block
                lprof_measurement_collection.add_obj(measure)
            for d_dict in data:
                d_dict = delete_nan_from_dict(d_dict)
                current_block = get_block(lprof_measurement_collection.block_collection.get_objs(), d_dict['block_id'], pid, tid) 
                measure = LprofMeasurement(self)
                measure.time_p = d_dict.get('time_p', None)
                measure.time_s = d_dict.get('time_s', None)
                measure.time_s_min= d_dict.get('time_s_min', None)
                measure.time_s_max = d_dict.get('time_s_max', None)
                measure.time_s_avg = d_dict.get('time_s_avg', None)
                measure.cov_deviation = d_dict.get('cov_deviation', None)
                measure.time_deviation = d_dict.get('time_deviation', None)
                measure.nb_threads = d_dict.get('nb_threads', None)
                measure.block = current_block
                lprof_measurement_collection.add_obj(measure)

        for file in function_files:
            lprof_pattern = r'lprof_functions_([\w\.]+)_(\d+)_(\d+).csv'
            data = read_file(self.visit_file(file)).to_dict(orient='records')
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
             #empty file
            if not data:
                current_function = get_function(lprof_measurement_collection.function_collection.get_objs(), None, pid, tid, None, None) 
                measure = LprofMeasurement(self)
                measure.function = current_function
                lprof_measurement_collection.add_obj(measure)
            for d_dict in data:
                d_dict = delete_nan_from_dict(d_dict)
                
                module = d_dict['module']
                function_name = d_dict['function_name']
                current_function = get_function(lprof_measurement_collection.function_collection.get_objs(), d_dict['function_id'], pid, tid, module, function_name) 
                measure = LprofMeasurement(self)
                measure.time_p = d_dict.get('time_p', None)
                measure.time_s = d_dict.get('time_s', None)
                measure.time_s_min= d_dict.get('time_s_min', None)
                measure.time_s_max = d_dict.get('time_s_max', None)
                measure.time_s_avg = d_dict.get('time_s_avg', None)
                measure.cov_deviation = d_dict.get('cov_deviation', None)
                measure.time_deviation = d_dict.get('time_deviation', None)
                measure.nb_threads = d_dict.get('nb_threads', None)
                measure.function = current_function
                lprof_measurement_collection.add_obj(measure)
        for file in loop_files:
            lprof_pattern = r'lprof_loops_([\w\.]+)_(\d+)_(\d+).csv'
            data = read_file(self.visit_file(file)).to_dict(orient='records')
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
             #empty file
            if not data:
                current_loop = get_loop(lprof_measurement_collection.loop_collection.get_objs(), None, pid, tid) 
                measure = LprofMeasurement(self)
                measure.loop = current_loop
                lprof_measurement_collection.add_obj(measure)
            for d_dict in data:
                d_dict = delete_nan_from_dict(d_dict)
                current_loop = get_loop(lprof_measurement_collection.loop_collection.get_objs(), d_dict['loop_id'], pid, tid) 
                measure = LprofMeasurement(self)
                measure.time_p = d_dict.get('time_p', None)
                measure.time_s = d_dict.get('time_s', None)
                measure.time_s_min= d_dict.get('time_s_min', None)
                measure.time_s_max = d_dict.get('time_s_max', None)
                measure.time_s_avg = d_dict.get('time_s_avg', None)
                measure.cov_deviation = d_dict.get('cov_deviation', None)
                measure.time_deviation = d_dict.get('time_deviation', None)
                measure.nb_threads = d_dict.get('nb_threads', None)
                measure.loop = current_loop

                lprof_measurement_collection.add_obj(measure)

    def visitCqaCollection(self, cqa_collection):
        cqa_dir_path, expert_loop_path = self.get_cqa_path()
        cqa_paths = get_files_with_extension(cqa_dir_path, ['.csv'])
        for cqa_path in cqa_paths:
            type, variant, module, identifier = parse_file_name(os.path.basename(cqa_path))

            current_loop = get_loop_by_maqao_id_module(self.get_current_execution(), int(identifier), module)

            cqa_df = read_file(self.visit_file(cqa_path))
            cqa_measures = []
            for index, row in cqa_df.iterrows():
                #cqa table
                path_id =  -1 if row['path ID'] == 'AVG' or row['path ID'] == 'NA' else int(row['path ID'])
                cqa_measure_obj = CqaMeasure(self)
                cqa_measure_obj.path_id = path_id
                cqa_measure_obj.loop = current_loop
                cqa_measure_obj.decan_variant = DecanVariant.get_or_create_by_name(variant, self)
                #cqa metrics
                row.pop('path ID')
                cqa_meatrics = cqa_measure_obj.add_metrics(self.session, row)
                cqa_measures.append(cqa_measure_obj)
                cqa_collection.add_obj(cqa_measure_obj)

             #analysis column for loop
            if not variant:
                loop_analysis_lua_file_name = '{}_{}_text.lua'.format(module, identifier)
                analysis_json_data = convert_lua_to_python(self.visit_file(os.path.join(cqa_dir_path,loop_analysis_lua_file_name)))
                current_cqa_analysis = CqaAnalysis.add_analysis(self.session, analysis_json_data)
                current_cqa_analysis.cqa_measures = cqa_measures

        #for the all fct cqa analysis create a cqa measure in the table
        cqa_fct_paths = get_files_starting_with_and_ending_with(cqa_dir_path, 'fct','text.lua')
        for cqa_path in cqa_fct_paths:
            type, variant, module, identifier = parse_file_name(os.path.basename(cqa_path))
            current_function = get_function_by_maqao_id_module(self.get_current_execution(), int(identifier), module)
            
             #create analysis col
            function_analysis_lua_file_name = 'fct_{}_{}_text.lua'.format(module, identifier)
            analysis_json_data = convert_lua_to_python(self.visit_file(os.path.join(cqa_dir_path,function_analysis_lua_file_name)))
            current_cqa_analysis = CqaAnalysis.add_analysis(self.session, analysis_json_data)

            ### for line in csv file create cqa measure, AVG = -1, function path id is -1
            cqa_measure_obj = CqaMeasure(self)
            cqa_measure_obj.path_id = -1
            cqa_measure_obj.cqa_analysis = current_cqa_analysis
            
            cqa_measure_obj.function = current_function
            cqa_collection.add_obj(cqa_measure_obj)



    def visitAsmCollection(self, asm_collection):
        asm_dir_path,_ = self.get_asm_path()
        asm_paths = get_files_with_extension(asm_dir_path, ['.csv'])
        for asm_path in asm_paths:
            type, variant, module, identifier = parse_file_name(os.path.basename(asm_path))
            asm_content = compress_file(self.visit_file(asm_path))

            asm_hash = get_file_sha256(asm_path)
            asm_obj = Asm(self)
            asm_obj.content = asm_content
            asm_obj.hash = asm_hash
            asm_obj.decan_variant = DecanVariant.get_or_create_by_name(variant, self)
           
            if type == 0:
                loop_obj = get_loop_by_maqao_id_module(self.get_current_execution(), int(identifier), module)
                asm_obj.loop = loop_obj
            else:
                function_obj = get_function_by_maqao_id_module(self.get_current_execution(), int(identifier), module)
                asm_obj.function = function_obj

            asm_collection.add_obj(asm_obj)
            self.session.flush()

    def visitGroupCollection(self, group_collection):
        group_dir_path = self.get_group_path()
        group_paths = get_files_with_extension(group_dir_path,['.csv'])
        for group_path in group_paths:
            type, variant, module, identifier = parse_file_name(os.path.basename(group_path))
            loop_obj = get_loop_by_maqao_id_module(self.get_current_execution(), int(identifier), module)
            group_data = get_data_from_csv(self.visit_file(group_path))

            if group_data is not None:
                for data in group_data:
                    group_obj = Group(self)
                    group_obj.group_size = data['group_size']
                    group_obj.pattern = data['pattern']
                    group_obj.opcodes = data['opcodes']
                    group_obj.offsets = data['offsets']
                    group_obj.addresses = data['addresses']
                    group_obj.stride_status = data['stride_status']
                    group_obj.stride = data['stride']
                    group_obj.memory_status = data['memory_status']
                    group_obj.accessed_memory = data['accessed_memory']
                    group_obj.accessed_memory_nooverlap = data['accessed_memory_nooverlap']
                    group_obj.accessed_memory_overlap = data['accessed_memory_overlap']
                    group_obj.span = data['span']
                    group_obj.head = data['head']
                    group_obj.unroll_factor = data['unroll_factor']
                    group_obj.loop = loop_obj
                    group_collection.add_obj(group_obj)

            else:
                group_obj = Group(self)
                group_obj.loop = loop_obj
                group_collection.add_obj(group_obj)

    def visitSourceCollection(self, source_collection):
        source_dir_path = self.get_source_path()
        source_paths = get_files_with_extension(source_dir_path,['txt'])
        for source_path in source_paths:
            type, variant, module, identifier = parse_file_name(os.path.basename(source_path))
            source_obj = Source(self)
            source_obj.content = compress_file(self.visit_file(source_path))
            source_obj.hash = get_file_sha256(source_path)
            if type == 0:
                loop_obj = get_loop_by_maqao_id_module(self.get_current_execution(), int(identifier), module)
                src_loop_obj = loop_obj.src_loop
                src_loop_obj.source = source_obj
            else:
                function_obj = get_function_by_maqao_id_module(self.get_current_execution(), int(identifier), module)
                src_function_obj = function_obj.src_function
                src_function_obj.source = source_obj

            source_collection.add_obj(source_obj)
    def visitCompilerCollection(self, compilerCollection):
        pass

class OneViewModelInitializerAndFileCopier(OneViewModelInitializer):
    def __init__(self, session, qaas_data_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id, output_path):
        super().__init__(session, qaas_data_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
        self.output_path = output_path

    def visit_file(self, file):
        #print(f"IN: {file}")
        rel_path = os.path.relpath(file, self.qaas_data_dir)
        outfile_path = os.path.join(self.output_path, rel_path)
        outfile_dir = os.path.dirname(outfile_path)
        os.makedirs(outfile_dir, exist_ok=True)
        shutil.copy(file, outfile_path)
        #print(f"OUT: {outfile_dir}")
        return super().visit_file(file)


#TODO write to part of the file
class OneViewModelExporter(OneviewModelAccessor):
    def __init__(self, session, qaas_data_dir):
        super().__init__(session, qaas_data_dir)
    def visitQaaSDataBase(self, qaas_database):
        pass
    def visitApplication(self, application):
        pass
  
 
    def visitExecution(self, execution, qaas_timestamp = None, version = None):
        local_vars_path, config_path, config_out_path, cqa_context_path, expert_run_path, log_path,lprof_log_path,fct_locations_path,\
            loop_locations_path, global_metrics_path, compilation_options_path, fct_callchain_path, loop_callchain_path = self.get_execution_path()
        # Create directories
        os.makedirs(os.path.dirname(local_vars_path), exist_ok=True)
        os.makedirs(os.path.dirname(config_out_path), exist_ok=True)
        os.makedirs(os.path.dirname(cqa_context_path), exist_ok=True)
        os.makedirs(os.path.dirname(expert_run_path), exist_ok=True)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        os.makedirs(os.path.dirname(lprof_log_path), exist_ok=True)
        os.makedirs(os.path.dirname(fct_locations_path), exist_ok=True)
        os.makedirs(os.path.dirname(loop_locations_path), exist_ok=True)
        os.makedirs(os.path.dirname(global_metrics_path), exist_ok=True)
        os.makedirs(os.path.dirname(compilation_options_path), exist_ok=True)
        os.makedirs(os.path.dirname(fct_callchain_path), exist_ok=True)
        os.makedirs(os.path.dirname(loop_callchain_path), exist_ok=True)
        #localvars csv
        create_or_update_localvar_df('is_src_code', str(execution.is_src_code).lower(), local_vars_path)
        create_or_update_localvar_df('universal_timestamp', execution.universal_timestamp, local_vars_path)
        create_or_update_localvar_df('timestamp', universal_timestamp_to_datetime(execution.universal_timestamp), local_vars_path)


        # config lua file and cqa_context lua
        convert_python_to_lua(execution.config, config_out_path) 
        convert_python_to_lua(execution.cqa_context, cqa_context_path) 
        #expert run csv
        expert_run_df = pd.DataFrame({'time': [execution.time],\
                            'profiled_time': [execution.profiled_time],\
                            'max_nb_threads': [execution.max_nb_threads]})
        write_file(expert_run_df, expert_run_path)
        ##log files
        with open(log_path, 'wb') as f:
            f.write(decompress_file(execution.log))
        with open(lprof_log_path, 'wb') as f:
            f.write(decompress_file(execution.lprof_log))
        # binaries files TODO

        #global metrics and compilation options
        global_metrics_df = pd.read_json(execution.global_metrics['global_metrics'], orient="split")
        
        if 'details' not in global_metrics_df.columns:
            global_metrics_df['details'] = np.nan
            columns = global_metrics_df.columns.tolist()
            columns.insert(-1, columns.pop(columns.index('details')))
            global_metrics_df = global_metrics_df[columns]

        compilation_options_df = pd.read_json(execution.global_metrics['compilation_options'], orient="split")
        write_file(global_metrics_df, global_metrics_path)
        write_file(compilation_options_df, compilation_options_path)

        ##output location binaries files
        convert_python_to_location_binary(execution.loop_location, loop_locations_path, self.session)
        convert_python_to_location_binary(execution.fct_location, fct_locations_path, self.session)
        ##output callchain bibnar files
        convert_callchain_python_to_binary(execution.loop_callchain, loop_callchain_path, self.session)
        convert_callchain_python_to_binary(execution.fct_callchain, fct_callchain_path, self.session)

        create_or_update_localvar_df('threads_per_core', execution.threads_per_core, local_vars_path)

    def visitOs(self, os_obj):
        local_vars_path=self.get_os_path()
        # Read existing data
        create_or_update_localvar_df('os_version', os_obj.os_version, local_vars_path)
        create_or_update_localvar_df('hostname', os_obj.hostname, local_vars_path)
        create_or_update_localvar_df('huge_pages', os_obj.huge_pages, local_vars_path)
        create_or_update_localvar_df('driver_frequency', os_obj.driver_frequency, local_vars_path)


    def visitMaqao(self, maqao):
        local_vars_path=self.get_maqao_path()
        # Read existing data
        create_or_update_localvar_df('global_instances_per_bucket', maqao.global_instances_per_bucket, local_vars_path)
        create_or_update_localvar_df('instances_per_bucket', maqao.instances_per_bucket, local_vars_path)
        create_or_update_localvar_df('architecture_code', maqao.architecture_code, local_vars_path)
        create_or_update_localvar_df('uarchitecture_code', maqao.uarchitecture_code, local_vars_path)
        create_or_update_localvar_df('min_time_obj', maqao.min_time_obj, local_vars_path)
        create_or_update_localvar_df('cqa_uarch', maqao.cqa_uarch, local_vars_path)
        create_or_update_localvar_df('cqa_arch', maqao.cqa_arch, local_vars_path)
        create_or_update_localvar_df('lprof_suffix', maqao.lprof_suffix, local_vars_path)
        create_or_update_localvar_df('last_html_path', maqao.last_html_path, local_vars_path)
        create_or_update_localvar_df('maqao_build', maqao.maqao_build, local_vars_path)
        create_or_update_localvar_df('maqao_version', maqao.maqao_version, local_vars_path)
        create_or_update_localvar_df('exp_version', maqao.exp_version, local_vars_path)
        create_or_update_localvar_df('nb_filtered_functions', maqao.nb_filtered_functions, local_vars_path)
        create_or_update_localvar_df('cov_filtered_loops', maqao.cov_filtered_loops, local_vars_path)
        create_or_update_localvar_df('nb_filtered_loops', maqao.nb_filtered_loops, local_vars_path)
        create_or_update_localvar_df('config_count', maqao.config_count, local_vars_path)
        create_or_update_localvar_df('cov_filtered_functions', maqao.cov_filtered_functions, local_vars_path)



    def visitHwSystem(self, hwsystem):
        local_vars_path=self.get_hwsystem_path()
        # Read existing data
        create_or_update_localvar_df('cpui_model_name', hwsystem.cpui_model_name, local_vars_path)
        create_or_update_localvar_df('cpui_cpu_cores', hwsystem.cpui_cpu_cores, local_vars_path)
        create_or_update_localvar_df('cpui_cache_size', hwsystem.cpui_cache_size, local_vars_path)
        create_or_update_localvar_df('cur_frequency', hwsystem.cur_frequency, local_vars_path)
        create_or_update_localvar_df('max_frequency', hwsystem.max_frequency, local_vars_path)
        create_or_update_localvar_df('architecture', hwsystem.architecture, local_vars_path)
        create_or_update_localvar_df('uarchitecture', hwsystem.uarchitecture, local_vars_path)
        create_or_update_localvar_df('proc_name', hwsystem.proc_name, local_vars_path)
        create_or_update_localvar_df('sockets', hwsystem.sockets, local_vars_path)
        create_or_update_localvar_df('cores_per_socket', hwsystem.cores_per_socket, local_vars_path)


     

    def visitEnvironment(self, environment):
        self.run_dir_path=self.get_env_path()
        # env_name = 'env_{}-{}.txt'.format(environment.execution.machine, environment.execution.os.hostname.tid)
        # create_file_from_metric_table(environment.environment_metrics, env_path)

    def visitDecanCollection(self, decan_collection):
        decan_path = self.get_decan_path()
        decan_data = []
        for decan in decan_collection.get_objs():
            metric = DecanMetric.get_metric_by_decan(decan, self)
            decan_dict = {
                'id' : decan.loop.maqao_loop_id,
                'module' : os.path.basename(decan.loop.function.module.name),
                'type' : decan.type,
                'variant' : decan.decan_variant.variant_name,
                'frequency' : decan.frequency,
                'bucket': decan.bucket,
                'mpi_process': decan.mpi_process,
                'thread' : decan.thread,
                'metric' : metric.metric_name,
                'value_type' : metric.metric_type,
                'value' : metric.metric_value
            }
            decan_data.append(decan_dict)

        decan_df = pd.DataFrame(decan_data)
        write_file(decan_df, decan_path)

    def visitVprofCollection(self, vprof_collection):
        vprof_path = self.get_vprof_path()
        vprof_data = []

        #module will be binary as a place holder, otter will rename it when generate the report
        for vprof in vprof_collection.get_objs():
            vprof_dict = {
                'loop_id' : vprof.loop.maqao_loop_id,
                'module' : "binary",
                'instance_count' : vprof.instance_count,
                'invalid_count' : vprof.invalid_count,
                'iteration_total' : vprof.iteration_total,
                'iteration_min' : vprof.iteration_min,
                'iteration_max' : vprof.iteration_max,
                'iteration_mean' : vprof.iteration_mean,
                'cycle_total' : vprof.cycle_total,
                'cycle_min' : vprof.cycle_min,
                'cycle_max' : vprof.cycle_max,
                'cycle_mean' : vprof.cycle_mean,
                'cycles_per_iteration_min' : vprof.cycles_per_iteration_min,
                'cycles_per_iteration_max' : vprof.cycles_per_iteration_max,
                'cycles_per_iteration_mean' : vprof.cycles_per_iteration_mean,
            }
            for vprof_bucket_measure in vprof.vprof_bucket_measures:
                bucket_range = vprof_bucket_measure.range_value
                vprof_dict['bucket_instance_percent_' + bucket_range] = vprof_bucket_measure.bucket_instance_percent
                vprof_dict['bucket_cycle_percent_' + bucket_range] = vprof_bucket_measure.bucket_cycle_percent
                vprof_dict['bucket_instances_' + bucket_range] = vprof_bucket_measure.bucket_instances
            vprof_data.append(vprof_dict)
            
        vprof_df = pd.DataFrame(vprof_data)
        write_file(vprof_df, vprof_path, delimiter=',')



    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        lprof_categorization_path1, lprof_categorization_path2 = self.get_lprof_categorization_path()
        os.makedirs(os.path.dirname(lprof_categorization_path1), exist_ok=True)
        os.makedirs(os.path.dirname(lprof_categorization_path2), exist_ok=True)

        lprof_categorization_list = []
        for lprof_categorization in lprof_categorization_collection.get_objs():
            lprof_categorization_dict = {
                'Node': lprof_categorization.node,
                'Process': lprof_categorization.process,
                'Thread': lprof_categorization.thread,
                'Nb Cycle Events': lprof_categorization.nb_cycle_events,
                'Time (s)': lprof_categorization.time_s
            }

            #metric data
            lprof_categorization_metrics = lprof_categorization.lprof_categorization_metrics
            names_and_values_data = get_names_and_values_data_for_metric_table(lprof_categorization_metrics)

            lprof_categorization_dict = {**lprof_categorization_dict, **names_and_values_data}
            lprof_categorization_list.append(lprof_categorization_dict)

        lprof_categorization_df = pd.DataFrame(lprof_categorization_list)
        write_file(lprof_categorization_df, lprof_categorization_path1)
        write_file(lprof_categorization_df, lprof_categorization_path2)


    def visitModuleCollection(self, module_collection):
        lprof_modules_path = self.get_module_path()
        os.makedirs(os.path.dirname(lprof_modules_path), exist_ok=True)

        lprof_list = []
        for module in module_collection.get_objs():
            module_dict = {
                'name' : module.name,
                'time_p' : module.time_p,
                'time_s' : module.time_s,
                'cpi_ratio' : module.cpi_ratio,
            }
            lprof_list.append(module_dict)
        
        lprof_df = pd.DataFrame(lprof_list)
        write_file(lprof_df, lprof_modules_path)

    
    def visitBlockCollection(self, block_collection):
        pass
      

    def visitFunctionCollection(self, function_collection):
        #TODO empty function 
        pass

    def visitLoopCollection(self, loop_collection):
        pass

    def get_measure_dict_by_measure_obj(self, measure):
        if measure:
            return {
                    'time_p': measure.time_p,
                    'time_s': measure.time_s,
                    'time_s_min': measure.time_s_min,
                    'time_s_max': measure.time_s_max,
                    'time_s_avg': measure.time_s_avg,
                    'cov_deviation': measure.cov_deviation,
                    'time_deviation': measure.time_deviation,
                    'nb_threads': measure.nb_threads

                }
        else:
           return None
    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        lprof_dir_path, expert_loop_path, hierarchy_dir_path = self.get_lprof_measurement_path()
        os.makedirs(os.path.dirname(expert_loop_path), exist_ok=True)
        os.makedirs(hierarchy_dir_path, exist_ok=True)

        blocks = lprof_measurement_collection.block_collection.get_objs()
        functions = lprof_measurement_collection.function_collection.get_objs()
        loops = lprof_measurement_collection.loop_collection.get_objs()

        overall_loop_info = [l for l in loops if l.pid == None and l.tid == None]
        loop_measurements = []
        for l in overall_loop_info:
            measurement = get_lprof_measure(lprof_measurement_collection.get_objs(), loop = l)
            if measurement is not None:
                loop_measurements.append(measurement)
        
        #expert loop.csv
        expert_df = pd.DataFrame()
        expert_df['ID'] = [f'Loop {m.loop.maqao_loop_id}' for m in loop_measurements]
        expert_df['Level'] = [level_map[m.loop.level]  for m in loop_measurements]
        expert_df['Module'] = [os.path.basename(m.loop.function.module.name) for m in loop_measurements]
        expert_df['Source Location'] = [f'{m.loop.src_loop.file}:{m.loop.src_loop.line_number}' for m in loop_measurements]
        expert_df['Source Function'] = [m.loop.function.function_name for m in loop_measurements]
        expert_df['Max Time Over Threads (s)'] = [m.time_s_min for m in loop_measurements]
        expert_df['Time w.r.t. Wall Time (s)'] = [m.time_s for m in loop_measurements]
        expert_df['Coverage (% app. time)'] = [m.time_p for m in loop_measurements]
        # CHECK: Level info missing from LProf data object
        accumulate_df(expert_df, ['ID'], expert_loop_path)

        ######create lprof files
        files = {}
        pid_tid_paris = set()
        machine_name = ""
        #blocks
        for block in blocks:
            machine_name = block.execution.os.hostname
            pid, tid = block.pid, block.tid
            #only add if they are nto None
            if pid and tid:
                pid_tid_paris.add((pid, tid))
            source_info = combine_source_info(block.file, block.line_number) if block.file and block.line_number else None
            if not pid and not tid:
                file_name = 'lprof_blocks.csv'
            else:
                file_name = 'lprof_blocks_{}_{}_{}.csv'.format(machine_name, pid, tid)
            if file_name not in files:
                files[file_name] = pd.DataFrame()
            block_dict = {
                'block_id':int(block.maqao_block_id) if block.maqao_block_id else None,
                'module':os.path.basename(block.module.name) if block.module else None,
                'source_info':source_info 
            }
            measure = get_lprof_measure(lprof_measurement_collection.get_objs(), block = block)
            self.add_dict_to_file(files, file_name, block_dict, measure)

        #functions
        not_created_pid_tid_pairs = pid_tid_paris.copy()
        for function in functions:
            pid, tid = function.pid, function.tid
            source_info = combine_source_info(function.src_function.file, function.src_function.line_number)  if function.src_function else None
            if not pid and not tid:
                file_name = 'lprof_functions.csv'
            else:
                file_name = f'lprof_functions_{machine_name}_{pid}_{tid}.csv'
            if file_name not in files:
                files[file_name] = pd.DataFrame()
            if (pid, tid) in not_created_pid_tid_pairs:
                not_created_pid_tid_pairs.remove((pid, tid))
            function_dict = {
                'function_id':int(function.maqao_function_id) if function.maqao_function_id else None,
                'module':os.path.basename(function.module.name) if function.module else None,
                'source_info':source_info,
                'function_name':function.function_name if function.function_name else None,
                'label_name':function.label_name if function.label_name else None,
                'cats':function.cats if function.cats else None
                }
            measure = get_lprof_measure(lprof_measurement_collection.get_objs(), function = function)
            self.add_dict_to_file(files, file_name, function_dict, measure)


        if not_created_pid_tid_pairs:
            for pid, tid in not_created_pid_tid_pairs:
                file_name = f'lprof_functions_{machine_name}_{pid}_{tid}.csv'
                function_dict = {
                    'function_id': None,
                    'module': None,
                    'source_info':None,
                    'function_name': None,
                    'label_name': None,
                    'cats': None
                }
                files[file_name] = pd.DataFrame()
                files[file_name] = add_dict_to_df(function_dict, files[file_name])


        #loops
        not_created_pid_tid_pairs = pid_tid_paris.copy()
        for loop in loops:
            pid, tid = loop.pid, loop.tid
            source_info = combine_source_info(loop.src_loop.file, loop.src_loop.line_number) if loop.src_loop else None
            if not pid and not tid:
                file_name = 'lprof_loops.csv'
            else:
                file_name = 'lprof_loops_{}_{}_{}.csv'.format(machine_name, pid, tid)
            if file_name not in files:
                files[file_name] = pd.DataFrame()
            if (pid, tid) in not_created_pid_tid_pairs:
                not_created_pid_tid_pairs.remove((pid, tid))
            loop_dict = {
                'loop_id':int(loop.maqao_loop_id) if loop.maqao_loop_id else None,
                'module':os.path.basename(loop.function.module.name) if loop.function else None,
                'source_info':source_info,
                'function_name':loop.function.function_name if loop.function else None, 
                'function_id':loop.function.maqao_function_id if loop.function else None, 
                'level':level_map[loop.level] if loop.level else None
                }
            if loop_dict['loop_id'] == 113:
                print(pid, tid)
            measure = get_lprof_measure(lprof_measurement_collection.get_objs(), loop = loop)
            self.add_dict_to_file(files, file_name, loop_dict, measure)

        #add left over empty pud and tid loop that cannot be got from any other objs    
        if not_created_pid_tid_pairs:
            for pid, tid in not_created_pid_tid_pairs:
                if not pid and not tid:
                    file_name = 'lprof_loops.csv'
                else:
                    file_name = f'lprof_loops_{machine_name}_{pid}_{tid}.csv'
                function_dict = {
                    'loop_id': None,
                    'module': None,
                    'source_info':None,
                    'function_name': None,
                    'function_id': None,
                    'level': None
                }
                files[file_name] = pd.DataFrame()
                files[file_name] = add_dict_to_df(function_dict, files[file_name])
        for file in files:
            file_path = os.path.join(lprof_dir_path, file)
            if is_df_empty(files[file]):
                write_file(files[file].head(0),file_path)
            else:
                write_file(files[file],file_path)

        #hierarchy files
        loop_functions = get_all_functions(lprof_measurement_collection.loop_collection)
        for function in loop_functions:
            if function:
                #hierarchy
                hierarchy_lua_file_name =  'fct_{}_{}.lua'.format(os.path.basename(function.module.name), function.maqao_function_id)
                os.makedirs(os.path.dirname(os.path.join(hierarchy_dir_path, hierarchy_lua_file_name)), exist_ok=True)

                convert_python_to_lua(function.hierarchy, os.path.join(hierarchy_dir_path, hierarchy_lua_file_name))

    def add_dict_to_file(self, files, file_name, block_dict, measure):
        measure_dict = self.get_measure_dict_by_measure_obj(measure)
            #TODO not a very good check if we don't have a measure dict just don't show entire line
        if measure_dict:
            merged_dict = {**block_dict, **measure_dict}
            files[file_name] = add_dict_to_df(merged_dict, files[file_name])

       
      
    def visitCqaCollection(self, cqa_collection):
        cqa_dir_path, expert_loop_path = self.get_cqa_path()
        os.makedirs(cqa_dir_path, exist_ok=True)
        loop_cqas = [cqa for cqa in cqa_collection.get_objs() if cqa.loop is not None]
        function_cqas = [cqa for cqa in cqa_collection.get_objs() if cqa.function is not None]

        avg_loop_cqas = [cqa for cqa in loop_cqas if cqa.path_id == -1]

        expert_df = pd.DataFrame()
        expert_df['ID'] = [f'Loop {cqa.loop.maqao_loop_id}' for cqa in avg_loop_cqas]
        expert_df['CQA cycles'] = [cqa.lookup_metric_unique('cycles L1') for cqa in avg_loop_cqas]
        expert_df['CQA cycles if no scalar integer'] = [cqa.lookup_metric_unique('cycles L1 if clean') for cqa in avg_loop_cqas]
        expert_df['Speedup if no scalar integer'] =[safe_division(cqa.lookup_metric_unique('CQA cycles'), cqa.lookup_metric_unique('CQA cycles if no scalar integer')) for cqa in avg_loop_cqas]
        expert_df['Vectorization Ratio (%)'] = [cqa.lookup_metric_unique('packed ratio all') for cqa in avg_loop_cqas]
        expert_df['Vectorization Efficiency (%)'] = [cqa.lookup_metric_unique('vec eff ratio all') for cqa in avg_loop_cqas]
        expert_df['Speedup if FP arith vectorized'] = [cqa.lookup_metric_unique('cycles L1 if FP arith vectorized') for cqa in avg_loop_cqas]
        expert_df['Speedup if fully vectorized'] = [cqa.lookup_metric_unique('cycles L1 if fully vectorized') for cqa in avg_loop_cqas]
        expert_df['Speedup if FP only'] = [cqa.lookup_metric_unique('cycles L1 if only FP') for cqa in avg_loop_cqas]
        expert_df['Number of paths'] = [cqa.lookup_metric_unique('nb paths') for cqa in avg_loop_cqas]
        expert_df['CQA cycles if FP arith vectorized'] = [cqa.lookup_metric_unique('cycles L1 if FP arith vectorized') for cqa in avg_loop_cqas]
        expert_df['CQA cycles if fully vectorized'] = [cqa.lookup_metric_unique('cycles L1 if fully vectorized') for cqa in avg_loop_cqas]
        expert_df['CQA cycles if FP only'] = [cqa.lookup_metric_unique('cycles L1 if only FP') for cqa in avg_loop_cqas]
    
        accumulate_df(expert_df, ['ID'], expert_loop_path)

        files = {}
        for cqa in loop_cqas:
            module_name = os.path.basename(cqa.loop.function.module.name)
            file_name = '{}_{}_{}_cqa.csv'.format(cqa.decan_variant.variant_name, module_name, cqa.loop.maqao_loop_id) if \
                    cqa.decan_variant is not None else '{}_{}_cqa.csv'.format(module_name, cqa.loop.maqao_loop_id)
            cqa_path = os.path.join(cqa_dir_path, file_name)

            if not cqa.decan_variant:
                #create the analysis lua file
                analysis_lua_file_name =  '{}_{}_text.lua'.format(module_name, cqa.loop.maqao_loop_id)
                analysis_path = os.path.join(cqa_dir_path, analysis_lua_file_name)
                if not os.path.exists(analysis_path):
                    analysis_python_data = cqa.cqa_analysis.analysis
                    convert_python_to_lua(analysis_python_data, analysis_path)
                    ##html lua files
                    analysis_html_lua_file_name = '{}_{}_html.lua'.format(module_name, cqa.loop.maqao_loop_id)
           
                    analysis_html_lua_path = os.path.join(cqa_dir_path, analysis_html_lua_file_name)
                    create_html_lua_by_text_python(analysis_python_data, analysis_html_lua_path) 

            ##create the cqa file for loop csv   
            if file_name not in files:
                files[file_name] = pd.DataFrame()
            path_id = cqa.path_id if cqa.path_id != -1 else 'AVG'
            cqa_metrics = get_names_and_values_data_for_metric_table(cqa.cqa_metrics)
            cqa_metrics['path ID'] = path_id
            files[file_name] = pd.concat([files[file_name], pd.DataFrame(cqa_metrics, index=[0])],axis=0, ignore_index=True)
        #write files
        for file in files:
            write_file(files[file], os.path.join(cqa_dir_path, file))


        for cqa in function_cqas:
            module_name = os.path.basename(cqa.function.module.name)
            analysis_lua_file_name =  'fct_{}_{}_text.lua'.format(module_name, cqa.function.maqao_function_id)
            convert_python_to_lua(cqa.cqa_analysis.analysis, os.path.join(cqa_dir_path, analysis_lua_file_name))
            ##html lua files
            analysis_html_lua_file_name = '{}_{}_html.lua'.format(module_name, cqa.function.maqao_function_id)
            analysis_html_lua_path = os.path.join(cqa_dir_path, analysis_html_lua_file_name)
            create_html_lua_by_text_python(cqa.cqa_analysis.analysis, analysis_html_lua_path) 



        
    def visitAsmCollection(self, asm_collection):
        asm_dir_path, asm_mapping_path = self.get_asm_path()
        os.makedirs(asm_dir_path, exist_ok=True)
        os.makedirs(asm_mapping_path, exist_ok=True)

        for asm in asm_collection.get_objs():

            #check if asm is function or loop
            if asm.loop: 

                module_name = os.path.basename(asm.loop.function.module.name)

                content = asm.content

                file_name = '{}_{}_{}.csv'.format(asm.decan_variant.variant_name, module_name, asm.loop.maqao_loop_id) if \
                    asm.decan_variant is not None else '{}_{}.csv'.format(module_name, asm.loop.maqao_loop_id)
                path = os.path.join(asm_dir_path, file_name)
                with open(path, 'wb') as f:
                    f.write(decompress_file(content))
            else:
                module_name = os.path.basename(asm.function.module.name)
                content = asm.content
                file_name = 'fct_{}_{}.csv'.format(module_name, asm.function.maqao_function_id)

                path = os.path.join(asm_dir_path, file_name)
                with open(path, 'wb') as f:
                    f.write(decompress_file(content))

    def visitSourceCollection(self, source_collection):
       source_dir_path = self.get_source_path()
       os.makedirs(source_dir_path, exist_ok=True)

       for source in source_collection.get_objs():
            if source.src_loops:
                loops = get_all_loops_from_src_loops(source.src_loops)
                loop = get_loop_by_source_loop(source.src_loops[0],loops)
                module_name = os.path.basename(loop.function.module.name)

                content = source.content
                file_name = 'src_{}_{}.txt'.format(module_name, loop.maqao_loop_id)
                path = os.path.join(source_dir_path, file_name)
                with open(path, 'wb') as f:
                    f.write(decompress_file(content))
            else:
                functions = get_all_functions_from_src_functions(source.src_functions)
                function = get_function_by_source_function(source.src_functions[0],functions)
                module_name = os.path.basename(function.module.name)

                content = source.content
                file_name = 'fct_{}_{}.txt'.format(module_name, function.maqao_function_id)
                path = os.path.join(source_dir_path, file_name)
                with open(path, 'wb') as f:
                    f.write(decompress_file(content))


    def visitGroupCollection(self, group_collection):
        group_dir_path = self.get_group_path()
        os.makedirs(group_dir_path, exist_ok=True)

        files = {}

        for group in group_collection.get_objs():
            module_name = os.path.basename(group.loop.function.module.name)
            maqao_id = group.loop.maqao_loop_id
            file_name =  '{}_{}.csv'.format(module_name, maqao_id)
            group_dict = {
                'group_size': group.group_size,
                'pattern': group.pattern,
                'opcodes': group.opcodes,
                'offsets': group.offsets,
                'addresses': group.addresses,
                'stride_status': group.stride_status,
                'stride': group.stride,
                'memory_status': group.memory_status,
                'accessed_memory': group.accessed_memory,
                'accessed_memory_nooverlap': group.accessed_memory_nooverlap,
                'accessed_memory_overlap': group.accessed_memory_overlap,
                'span': group.span,
                'head': group.head,
                'unroll_factor': group.unroll_factor,
            }

            if file_name not in files:
                files[file_name] = []

            files[file_name].append(group_dict)

        for file in files:
            group_df = pd.DataFrame(files[file])
            file_path = os.path.join(group_dir_path, file)
            if is_df_empty(group_df):
                write_file(group_df.head(0),file_path)
            else:
                write_file(group_df,file_path)
    def visitCompilerCollection(self, compilerCollection):
        pass



#this class is used to find a specfic metrc throught the execution
class MetricGetter(ModelAccessor):
    def __init__(self, session, metric_type, model_obj):
        super().__init__(session)
        self.metric_type = metric_type
        self.model_obj = model_obj
        self.data = None 

    #get value for execution
    def get_value(self):
        self.model_obj.accept(self)  
        return self.data


    def visitExecution(self, execution):
        # Create a dictionary mapping the metric type to the corresponding value
        global_metrics = get_global_metrics_dict_from_execution(execution)
        metric_mapper = {
            'total_time': execution.time,
            'array_access_efficiency': global_metrics['array_access_efficiency'],
            'profiled_time': execution.profiled_time,
            'number_of_cores': execution.hwsystem.cpui_cpu_cores,
            'speedup_if_clean': global_metrics['speedup_if_clean'],
            'speedup_if_fp_vect': global_metrics['speedup_if_fp_vect'],
            'speedup_if_fully_vectorised': global_metrics['speedup_if_fully_vectorised'],
            'speedup_if_FP_only': global_metrics['speedup_if_FP_only'],
            'model_name': execution.hwsystem.cpui_model_name,
            'time_in_analyzed_loops': global_metrics['loops_time'],
            'time_in_analyzed_innermost_loops': global_metrics['innerloops_time'],
            'time_in_user_code': global_metrics['user_time'],
            'compilation_options_score': global_metrics['compilation_options'],
            'perfect_flow_complexity': global_metrics['flow_complexity'],
            'perfect_openmp_mpi_pthread': global_metrics['speedup_if_perfect_MPI_OMP_PTHREAD'],
            'perfect_openmp_mpi_pthread_load_distribution': global_metrics['speedup_if_perfect_MPI_OMP_PTHREAD_LOAD_DISTRIBUTION'],
            'compilation_flags': global_metrics['compilation_flags'],
            'iterations_count': global_metrics['iterations_count'],
            'speedup_if_L1': global_metrics['speedup_if_L1'],
            'program': execution.application.program,
            'experiment_name': execution.application.version,

        }

        value = metric_mapper.get(self.metric_type)
        self.data = value



    def visitCqaCollection(self, cqa_collection):
        loop_cqas = [cqa for cqa in cqa_collection.get_objs() if cqa.loop is not None]
        res = []
        for cqa in loop_cqas:
            cqa_metrics = get_names_and_values_data_for_metric_table(cqa.cqa_metrics)

            #vectorization ratio
            if self.metric_type == "vectorization_ratio":
                metric_value = cqa_metrics.get('packed ratio all')

            #vectorization efficiency
            if self.metric_type == "vectorization_efficiency":
                metric_value = cqa_metrics.get('vec eff ratio all')

            if metric_value:
                res.append(metric_value)
            self.data = res 

    def visitQaaSDataBase(self, qaas_database):
        pass
    def visitApplication(self, application):
        pass
    def visitEnvironment(self, environment):
        pass
    def visitOs(self, os):
        pass
    def visitHwSystem(self, hwsystem):
        pass
    def visitMaqao(self, maqao):
        pass
    def visitDecanCollection(self, decan_collection):
        pass
    def visitVprofCollection(self, vprof_collection):
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
    def visitAsmCollection(self, asm_collection):
        pass
    def visitGroupCollection(self, group_collection):
        pass
    def visitSourceCollection(self, source_collection):
        pass
    def visitCompilerCollection(self, compilerCollection):
        pass