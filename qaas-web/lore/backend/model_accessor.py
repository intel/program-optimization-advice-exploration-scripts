from abc import ABC, abstractmethod
from util import *
import os
import pandas as pd
from model import *
from model_collection import *
import csv
import time
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
            current_application = Application(self)
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
        self.lore_data_path = '/nfs/site/proj/alac/data/UIUC-LORE/codelets/loop_collections_12072018'

        #iterate all the executions 
        with open(os.path.join(self.lore_csv_dir, 'executions.csv'), 'r') as file:
            csv_reader = csv.DictReader(file, delimiter=',')
            for i, row in enumerate(csv_reader):
                # if i == 1000:
                #     break
                #create execution obj for each execution
                self.current_execution_data = row
                current_execution = Execution(self)
                if i % 100 == 0:
                    print(i)

        end_time = time.time()

        total_execution_time = end_time - start_time
        print(f"The program took {total_execution_time} seconds to run.")


            
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
            print(source_code_file_name, "does not exist")
            return
        cleaned_data_loop = delete_data_from_dict(orig_src_loop_dict, self.unneeded_columns_loop)
        current_src = Source.get_or_create_source_by_hash(source_code_path, cleaned_data_loop, self)
        

        #create src loop obj for each execution
        current_src_loop = SrcLoop(self)

        source_code_line_number = get_mutation_line_number(source_code_path)
        current_src_loop.file = source_code_file_name
        current_src_loop.line_number = source_code_line_number

        current_src_loop.source = current_src
        current_src_loop.mutation_number = mutation_number
        current_src_loop.execution = current_execution
        
        #link to mutation
        current_mutation = self.find_mutation_by_loop_id_and_mutation_number(lookup_key)
        assert current_mutation is not None, "Using id + mutation number to get mutation, but retrieved values is None"
        current_src_loop.mutation = current_mutation

        #create and link to loop
        current_loop = Loop(self)
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


class OneviewModelAccessor(ModelAccessor):
    def __init__(self, session, qaas_data_dir):
        super().__init__(session)
        self.qaas_data_dir = qaas_data_dir
        self.cur_run_id = 0
        self.static_dir_path = os.path.join(self.qaas_data_dir, "static_data")
        self.run_dir_path = os.path.join(self.qaas_data_dir, "shared", self.get_run_name())

        self.log_dir = os.path.join(self.qaas_data_dir, 'logs')
        self.source_dir = os.path.join(self.static_dir_path, "sources")
        self.lprof_dir_path = os.path.join(self.qaas_data_dir, "shared",f"lprof_npsu_{self.get_run_name()}")
        self.hierarchy_dir_path = os.path.join(self.static_dir_path, 'hierarchy')
        self.callchain_dir_path = os.path.join(self.lprof_dir_path, 'callchains')

        self.local_vars_path1 = os.path.join(self.static_dir_path, 'local_vars.csv')
        self.local_vars_path2 = os.path.join(self.run_dir_path, 'local_vars.csv')
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

        return self.local_vars_path1, self.local_vars_path2, config_path, cqa_context_path, expert_run_path, log_path,lprof_log_path,\
                fct_locations_path,loop_locations_path, global_metrics_path, compilation_options_path, fct_callchain_path, loop_callchain_path
    
    def get_os_path(self):
        return self.local_vars_path1, self.local_vars_path2

    def get_hwsystem_path(self):
        return self.local_vars_path1, self.local_vars_path2

    
    def get_maqao_path(self):
        return self.local_vars_path1, self.local_vars_path2
    
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
        return asm_dir_path
    def get_group_path(self):
        group_dir_path = os.path.join(self.static_dir_path, "groups")
        return group_dir_path
    def get_source_path(self):
        source_dir_path = os.path.join(self.static_dir_path, "sources")
        return source_dir_path

   
   

class OneViewModelInitializer(OneviewModelAccessor):
    def __init__(self, session, qaas_data_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id):
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
    
   
    def visitQaaSDataBase(self, qaas_database):
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

        # # ###maqao table
        current_maqao = Maqao( self)
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
    
        

    def visitEnvironment(self, environment):
        self.run_dir_path=self.get_env_path()

        env_path = get_files_starting_with_and_ending_with(self.run_dir_path, 'env_','.txt')[0]

        env_data = convert_text_to_dict(env_path)
        
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
        local_vars_path1, local_vars_path2, config_path, cqa_context_path, expert_run_path, log_path,lprof_log_path,\
            fct_locations_path,loop_locations_path, global_metrics_path, compilation_options_path, fct_callchain_path, loop_callchain_path = self.get_execution_path()
        local_vars_dict = read_file(local_vars_path1).to_dict(orient='records')[0]

        execution.is_src_code = local_vars_dict['is_src_code']
        execution.universal_timestamp = local_vars_dict['universal_timestamp']

        #add additional cols
        execution.is_orig = 1 if execution.version == 'orig' else 0
        # #config lua and cqa_context
        execution.config = convert_lua_to_python(config_path)
        execution.cqa_context = convert_lua_to_python(cqa_context_path)
        
        # #get time, profiled time, and max_nb_threads from expert loops
        expert_run_data = get_data_from_csv(expert_run_path)[0]
        execution.time = expert_run_data['time']
        execution.profiled_time = expert_run_data['profiled_time']
        execution.max_nb_threads = expert_run_data['max_nb_threads']

        # #get log files
        execution.log = compress_file(log_path)
        execution.lprof_log = compress_file(lprof_log_path)

        # #get src location for fct and loop
        # #get the location binary files
        source_loop_python_obj = convert_location_binary_to_python(loop_locations_path, self.session)
        source_fct_python_obj = convert_location_binary_to_python(fct_locations_path, self.session)
        execution.fct_location = source_fct_python_obj
        execution.loop_location = source_loop_python_obj

        ##callchain binary
        callchain_fct_python_obj = convert_callchain_binary_to_python(fct_callchain_path, self.session)
        callchain_loop_python_obj = convert_callchain_binary_to_python(loop_callchain_path, self.session)
        execution.fct_callchain = callchain_fct_python_obj
        execution.loop_callchain = callchain_loop_python_obj
        ##global metrics
        global_metrics_df = read_file(global_metrics_path)
        compilation_options_df = read_file(compilation_options_path)
        global_metrics_dict={
            'global_metrics': global_metrics_df.to_json(orient="split"),
            'compilation_options': compilation_options_df.to_json(orient="split")
        }
        execution.global_metrics = global_metrics_dict


    def visitOs(self, os):
        local_vars_path1, local_vars_path2=self.get_os_path()
        local_vars_dict = read_file(local_vars_path1).to_dict(orient='records')[0]
        os.os_version = local_vars_dict['os_version']
        os.hostname = local_vars_dict['hostname']
        

    def visitHwSystem(self, hwsystem):
        local_vars_path1, local_vars_path2=self.get_os_path()
        local_vars_dict = read_file(local_vars_path1).to_dict(orient='records')[0]
        hwsystem.cpui_model_name =  local_vars_dict['cpui_model_name']
        hwsystem.cpui_cpu_cores = local_vars_dict['cpui_cpu_cores']
        hwsystem.cpui_cache_size =  local_vars_dict['cpui_cache_size']
        hwsystem.cur_frequency =  local_vars_dict['cur_frequency']
        hwsystem.max_frequency = local_vars_dict['max_frequency']
        hwsystem.architecture =  local_vars_dict['architecture']
        hwsystem.uarchitecture =  local_vars_dict['uarchitecture']
        hwsystem.proc_name =  local_vars_dict['proc_name']

    def visitMaqao(self, maqao):
        local_vars_path1, local_vars_path2=self.get_os_path()
        local_vars_dict = read_file(local_vars_path1).to_dict(orient='records')[0]
        maqao.global_instances_per_bucket = local_vars_dict['global_instances_per_bucket']
        maqao.instances_per_bucket = local_vars_dict['instances_per_bucket']
        maqao.architecture_code = local_vars_dict['architecture_code']
        maqao.uarchitecture_code = local_vars_dict['uarchitecture_code']
        maqao.min_time_obj =local_vars_dict['min_time_obj']
        maqao.cqa_uarch = local_vars_dict['cqa_uarch']
        maqao.cqa_arch = local_vars_dict['cqa_arch']
        maqao.lprof_suffix = local_vars_dict['lprof_suffix']
        maqao.last_html_path = local_vars_dict['last_html_path']
        maqao.maqao_build = local_vars_dict['maqao_build']
        maqao.maqao_version = local_vars_dict['maqao_version']
        maqao.exp_version = local_vars_dict['exp_version']

    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        lprof_categorization_path1, lprof_categorization_path2 = self.get_lprof_categorization_path()
        lprof_categorization_csv_df = read_file(lprof_categorization_path1)
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
        lprof_df = read_file(lprof_path)
        module_data_list = get_table_data_from_df(lprof_df, Module)
        for data in module_data_list:
            data = delete_nan_from_dict(data)
            module = Module(self)
            module.name = data.get('name', None)
            module.time_p = data.get('time_p',None)
            module.time_s = data.get('time_s',None)
            module.cpi_ratio = data.get('cpi_ratio', None)
            module_collection.add_obj(module)

    def visitBlockCollection(self, block_collection):
        lprof_dir_path = self.get_block_path()
        lprof_pattern = r'lprof_blocks_(\w+)_(\d+)_(\d+).csv'
        #pid and tid null means overall measurement
        files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_blocks', '.csv')
        for file in files:
            #check if there is pid and tid in the file name
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
                
            data = read_file(file).to_dict(orient='records')
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
                    source_name, line_number = d_dict['source_info'].split(':')
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
        lprof_pattern = r'lprof_functions_(\w+)_(\d+)_(\d+).csv'
        files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_functions', '.csv')
        for file in files:
            data = read_file(file).to_dict(orient='records')
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
                    if not is_nan(d_dict['source_info']): 
                        source_file, line_number = d_dict['source_info'].split(':')
                        src_function = SrcFunction(self)
                        src_function.file = source_file
                        src_function.line_number = line_number
                        src_function.execution = self.get_current_execution()

                    #function
                    module_name = d_dict['module']
                    current_module = get_module_by_name(self.get_current_execution().modules, module_name)
                    current_function = Function(self)
                    current_function.function_name = d_dict['function_name']
                    current_function.label_name=d_dict['label_name']
                    current_function.maqao_function_id = d_dict['function_id']
                    current_function.cats = d_dict['cats']
                    current_function.pid = pid
                    current_function.tid = tid 
                    current_function.module =  current_module  
                    current_function.src_function = src_function
                    function_collection.add_obj(current_function)

    def visitLoopCollection(self, loop_collection):
        lprof_dir_path, hierarchy_dir_path = self.get_loop_path()
        lprof_pattern = r'lprof_loops_(\w+)_(\d+)_(\d+).csv'
        files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_loops', '.csv')
        for file in files:
            data = read_file(file).to_dict(orient='records')
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
                if not is_nan(d_dict['source_info']): 
                    source_file, line_number = d_dict['source_info'].split(':')
                    src_loop = SrcLoop(self)
                    src_loop.file = source_file
                    src_loop.line_number = line_number
                    src_loop.execution = self.get_current_execution()

                #loop
                d_dict['level'] = reverse_level_map[d_dict['level']]
                current_loop = Loop(self)
                current_loop.maqao_loop_id = d_dict['loop_id']
                current_loop.level = d_dict['level']
                
                current_loop.pid = pid
                current_loop.tid = tid 

                maqao_function_id = d_dict['function_id']
                current_function = get_function_by_maqao_id(self.get_current_execution(), maqao_function_id)  
                current_loop.src_loop = src_loop
                current_loop.function = current_function
                loop_collection.add_obj(current_loop)

        #create cqa hierarch column
        loop_functions = get_all_functions(loop_collection)
        for function in loop_functions:
            if function:
                hierarchy_file_name = 'fct_{}_{}.lua'.format(os.path.basename(function.module.name), d_dict['function_id'])
                hierarchy_file_path = os.path.join(hierarchy_dir_path,hierarchy_file_name)
                hierarchy_json_data = convert_lua_to_python(hierarchy_file_path)
                function.hierarchy = hierarchy_json_data


        
    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        lprof_dir_path, expert_loop_path, hierarchy_dir_path = self.get_lprof_measurement_path()
        block_files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_blocks', '.csv')
        function_files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_functions', '.csv')
        loop_files = get_files_starting_with_and_ending_with(lprof_dir_path, 'lprof_loops', '.csv')
        #TODO read pid tid file and lprof_blocks.cs separately
        for file in block_files:
            lprof_pattern = r'lprof_blocks_(\w+)_(\d+)_(\d+).csv'
            data = read_file(file).to_dict(orient='records')
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
            lprof_pattern = r'lprof_functions_(\w+)_(\d+)_(\d+).csv'
            data = read_file(file).to_dict(orient='records')
            match = re.match(lprof_pattern, os.path.basename(file))
            if match:
                pid, tid = int(match.group(2)), int(match.group(3))
            else:
                pid, tid = None, None
             #empty file
            if not data:
                current_function = get_function(lprof_measurement_collection.function_collection.get_objs(), None, pid, tid) 
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
            lprof_pattern = r'lprof_loops_(\w+)_(\d+)_(\d+).csv'
            data = read_file(file).to_dict(orient='records')
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
            _, module, identifier = parse_file_name_no_variant(os.path.basename(cqa_path))
            current_loop = get_loop_by_maqao_id(self.get_current_execution(), int(identifier))
            
            #analysis column for loop
            loop_analysis_lua_file_name = '{}_{}_text.lua'.format(module, identifier)
            analysis_json_data = convert_lua_to_python(os.path.join(cqa_dir_path,loop_analysis_lua_file_name))
            current_cqa_analysis = CqaAnalysis.add_analysis(self.session, analysis_json_data)

            cqa_df = read_file(cqa_path)
            cqa_measures = []
            for index, row in cqa_df.iterrows():
                #cqa table
                path_id =  -1 if row['path ID'] == 'AVG' else int(row['path ID'])
                cqa_measure_obj = CqaMeasure(self)
                cqa_measure_obj.path_id = path_id
                cqa_measure_obj.loop = current_loop
                #cqa metrics
                row.pop('path ID')
                cqa_meatrics = cqa_measure_obj.add_metrics(self.session, row)
                cqa_measures.append(cqa_measure_obj)
                cqa_collection.add_obj(cqa_measure_obj)
            current_cqa_analysis.cqa_measures = cqa_measures

        #for the all fct cqa analysis create a cqa measure in the table
        cqa_fct_paths = get_files_starting_with_and_ending_with(cqa_dir_path, 'fct','text.lua')
        for cqa_path in cqa_fct_paths:
            _, module, identifier = parse_file_name_no_variant(os.path.basename(cqa_path))
            current_function = get_function_by_maqao_id(self.get_current_execution(), int(identifier))
            
             #create analysis col
            function_analysis_lua_file_name = 'fct_{}_{}_text.lua'.format(module, identifier)
            analysis_json_data = convert_lua_to_python(os.path.join(cqa_dir_path,function_analysis_lua_file_name))
            current_cqa_analysis = CqaAnalysis.add_analysis(self.session, analysis_json_data)

            ### for line in csv file create cqa measure, AVG = -1, function path id is -1
            cqa_measure_obj = CqaMeasure(self)
            cqa_measure_obj.path_id = -1
            cqa_measure_obj.cqa_analysis = current_cqa_analysis
            
            cqa_measure_obj.function = current_function
            cqa_collection.add_obj(cqa_measure_obj)



    def visitAsmCollection(self, asm_collection):
        asm_dir_path = self.get_asm_path()
        asm_paths = get_files_with_extension(asm_dir_path, ['.csv'])
        for asm_path in asm_paths:
            type, module, identifier = parse_file_name_no_variant(os.path.basename(asm_path))
            asm_content = compress_file(asm_path)
            asm_hash = get_file_sha256(asm_path)
            asm_obj = Asm(self)
            asm_obj.content = asm_content
            asm_obj.hash = asm_hash

            if type == 0:
                loop_obj = get_loop_by_maqao_id(self.get_current_execution(), int(identifier))
                loop_obj.asm = asm_obj
            else:
                function_obj = get_function_by_maqao_id(self.get_current_execution(), int(identifier))
                function_obj.asm = asm_obj

            asm_collection.add_obj(asm_obj)

    def visitGroupCollection(self, group_collection):
        group_dir_path = self.get_group_path()
        group_paths = get_files_with_extension(group_dir_path,['.csv'])
        for group_path in group_paths:
            type, module, identifier = parse_file_name_no_variant(os.path.basename(group_path))
            loop_obj = get_loop_by_maqao_id(self.get_current_execution(), int(identifier))
            group_data = get_data_from_csv(group_path)

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
                group_obj = Group()
                group_obj.loop = loop_obj
                group_collection.add_obj(group_obj)

    def visitSourceCollection(self, source_collection):
        source_dir_path = self.get_source_path()
        source_paths = get_files_with_extension(source_dir_path,['txt'])
        for source_path in source_paths:
            type, module, identifier = parse_file_name_no_variant(os.path.basename(source_path))
            source_obj = Source(self)
            source_obj.content = compress_file(source_path)
            source_obj.hash = get_file_sha256(source_path)
            if type == 0:
                loop_obj = get_loop_by_maqao_id(self.get_current_execution(), int(identifier))
                src_loop_obj = loop_obj.src_loop
                src_loop_obj.source = source_obj
            else:
                function_obj = get_function_by_maqao_id(self.get_current_execution(), int(identifier))
                src_function_obj = function_obj.src_function
                src_function_obj.source = source_obj

            source_collection.add_obj(source_obj)

#TODO write to part of the file
class OneViewModelExporter(OneviewModelAccessor):
    def __init__(self, session, qaas_data_dir):
        super().__init__(session, qaas_data_dir)
    def visitQaaSDataBase(self, qaas_database):
        pass
    def visitApplication(self, application):
        pass
    def visitExecution(self, execution, qaas_timestamp = None, version = None):
        local_vars_path1, local_vars_path2, config_path, cqa_context_path, expert_run_path, log_path,lprof_log_path,fct_locations_path,\
            loop_locations_path, global_metrics_path, compilation_options_path, fct_callchain_path, loop_callchain_path = self.get_execution_path()
        # Create directories
        os.makedirs(os.path.dirname(local_vars_path1), exist_ok=True)
        os.makedirs(os.path.dirname(local_vars_path2), exist_ok=True)
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
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
        local_vars_df = get_or_create_df(local_vars_path1)
        local_vars_df.loc[0, 'is_src_code'] = execution.is_src_code
        local_vars_df.loc[0, 'universal_timestamp'] = execution.universal_timestamp
        local_vars_df.loc[0, 'timestamp'] = universal_timestamp_to_datetime(execution.universal_timestamp)
        write_file(local_vars_df, local_vars_path1)
        write_file(local_vars_df, local_vars_path2)

        # config lua file and cqa_context lua
        convert_python_to_lua(execution.config, config_path) 
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
        compilation_options_df = pd.read_json(execution.global_metrics['compilation_options'], orient="split")
        write_file(global_metrics_df, global_metrics_path)
        write_file(compilation_options_df, compilation_options_path)

        ##output location binaries files
        convert_python_to_location_binary(execution.loop_location, loop_locations_path, self.session)
        convert_python_to_location_binary(execution.fct_location, fct_locations_path, self.session)
        ##output callchain bibnar files
        convert_callchain_python_to_binary(execution.loop_callchain, loop_callchain_path, self.session)
        convert_callchain_python_to_binary(execution.fct_callchain, fct_callchain_path, self.session)

    def visitOs(self, os_obj):
        local_vars_path1, local_vars_path2=self.get_os_path()
        # Read existing data
        local_vars_df = get_or_create_df(local_vars_path1)
        # Update the data
        #use pd.merge
        local_vars_df.loc[0,'os_version'] = os_obj.os_version
        local_vars_df.loc[0,'hostname'] = os_obj.hostname

        # Write the data back to the file
        write_file(local_vars_df, local_vars_path1)
        write_file(local_vars_df, local_vars_path2)

    def visitMaqao(self, maqao):
        local_vars_path1, local_vars_path2=self.get_maqao_path()
        # Read existing data
        local_vars_df = get_or_create_df(local_vars_path1)


        # Update the data
        #use pd.merge
        local_vars_df.loc[0, 'global_instances_per_bucket'] = maqao.global_instances_per_bucket
        local_vars_df.loc[0, 'instances_per_bucket'] = maqao.instances_per_bucket
        local_vars_df.loc[0, 'architecture_code'] = maqao.architecture_code
        local_vars_df.loc[0, 'uarchitecture_code'] = maqao.uarchitecture_code
        local_vars_df.loc[0, 'min_time_obj'] = maqao.min_time_obj
        local_vars_df.loc[0, 'cqa_uarch'] = maqao.cqa_uarch
        local_vars_df.loc[0, 'cqa_arch'] = maqao.cqa_arch
        local_vars_df.loc[0, 'lprof_suffix'] = maqao.lprof_suffix
        local_vars_df.loc[0, 'last_html_path'] = maqao.last_html_path
        local_vars_df.loc[0, 'maqao_build'] = maqao.maqao_build
        local_vars_df.loc[0, 'maqao_version'] = maqao.maqao_version
        local_vars_df.loc[0, 'exp_version'] = maqao.exp_version

        # Write the data back to the file
        write_file(local_vars_df, local_vars_path1)
        write_file(local_vars_df, local_vars_path2)
    def visitHwSystem(self, hwsystem):
        local_vars_path1, local_vars_path2=self.get_os_path()
        # Read existing data
        local_vars_df = get_or_create_df(local_vars_path1)


        # Update the data
        #use pd.merge
        local_vars_df.loc[0, 'cpui_model_name'] = hwsystem.cpui_model_name
        local_vars_df.loc[0, 'cpui_cpu_cores'] = hwsystem.cpui_cpu_cores
        local_vars_df.loc[0, 'cpui_cache_size'] = hwsystem.cpui_cache_size
        local_vars_df.loc[0, 'cur_frequency'] = hwsystem.cur_frequency
        local_vars_df.loc[0, 'max_frequency'] = hwsystem.max_frequency
        local_vars_df.loc[0, 'architecture'] = hwsystem.architecture
        local_vars_df.loc[0, 'uarchitecture'] = hwsystem.uarchitecture
        local_vars_df.loc[0, 'proc_name'] = hwsystem.proc_name

        # Write the data back to the file
        write_file(local_vars_df, local_vars_path1)
        write_file(local_vars_df, local_vars_path2)
    def visitEnvironment(self, environment):
        self.run_dir_path=self.get_env_path()
        # env_name = 'env_{}-{}.txt'.format(environment.execution.machine, environment.execution.os.hostname.tid)
        # create_file_from_metric_table(environment.environment_metrics, env_path)

    def visitLprofCategorizationCollection(self, lprof_categorization_collection):
        lprof_categorization_path1, lprof_categorization_path2 = self.get_lprof_categorization_path()
        os.makedirs(os.path.dirname(lprof_categorization_path1), exist_ok=True)
        os.makedirs(os.path.dirname(lprof_categorization_path2), exist_ok=True)

        lprof_categorization_df = pd.DataFrame()
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
            lprof_categorization_df = lprof_categorization_df.append(lprof_categorization_dict, ignore_index=True)
        write_file(lprof_categorization_df, lprof_categorization_path1)
        write_file(lprof_categorization_df, lprof_categorization_path2)

    def visitModuleCollection(self, module_collection):
        lprof_modules_path = self.get_module_path()
        os.makedirs(os.path.dirname(lprof_modules_path), exist_ok=True)

        lprof_df = pd.DataFrame()
        for module in module_collection.get_objs():
            module_dict = {
                'name' : module.name,
                'time_p' : module.time_p,
                'time_s' : module.time_s,
                'cpi_ratio' : module.cpi_ratio,
            }
            lprof_df = lprof_df.append(module_dict, ignore_index=True)
        write_file(lprof_df,lprof_modules_path)
    
    def visitBlockCollection(self, block_collection):
        pass
    
    def visitCompilerCollection(self, compiler_collection):
        pass

    def visitFunctionCollection(self, function_collection):
        #TODO empty function 
        pass

    def visitLoopCollection(self, loop_collection):
        pass

    def get_measure_dict_by_measure_obj(self, measure):
        if measure:
            measure_dict = {
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
            measure_dict = {
                    'time_p': None,
                    'time_s': None,
                    'time_s_min': None,
                    'time_s_max': None,
                    'time_s_avg': None,
                    'cov_deviation': None,
                    'time_deviation': None,
                    'nb_threads': None

                }
        return measure_dict
    def visitLprofMeasurementCollection(self, lprof_measurement_collection):
        lprof_dir_path, expert_loop_path, hierarchy_dir_path = self.get_lprof_measurement_path()
        os.makedirs(os.path.dirname(expert_loop_path), exist_ok=True)
        os.makedirs(os.path.dirname(hierarchy_dir_path), exist_ok=True)

        blocks = lprof_measurement_collection.block_collection.get_objs()
        functions = lprof_measurement_collection.function_collection.get_objs()
        loops = lprof_measurement_collection.loop_collection.get_objs()

        overall_loop_info = [l for l in loops if l.pid == None and l.tid == None]
        loop_measurements = [get_lprof_measure(lprof_measurement_collection.get_objs(), loop = l) for l in overall_loop_info ]

        #expert loop.csv
        expert_df = pd.DataFrame()
        expert_df['ID'] = [f'Loop {m.loop.maqao_loop_id}' for m in loop_measurements]
        expert_df['Level'] = [level_map[l.level]  for l in overall_loop_info]
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
            pid_tid_paris.add((pid, tid))
            source_info = f'{block.file}:{block.line_number}' if block.file and block.line_number else None
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
            measure_dict = self.get_measure_dict_by_measure_obj(measure)
            merged_dict = {**block_dict, **measure_dict}
            files[file_name] = add_dict_to_df(merged_dict, files[file_name])

        #functions
        not_created_pid_tid_pairs = pid_tid_paris.copy()
        for function in functions:
            pid, tid = function.pid, function.tid
            source_info = f'{function.src_function.file}:{function.src_function.line_number}' if function.src_function else None
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
            measure_dict = self.get_measure_dict_by_measure_obj(measure)
            merged_dict = {**function_dict, **measure_dict}

            files[file_name] = add_dict_to_df(merged_dict, files[file_name])

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
            source_info = '{}:{}'.format(loop.src_loop.file, loop.src_loop.line_number) if loop.src_loop else None
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
            measure = get_lprof_measure(lprof_measurement_collection.get_objs(), loop = loop)
            measure_dict = self.get_measure_dict_by_measure_obj(measure)
            merged_dict = {**loop_dict, **measure_dict}
            files[file_name] = add_dict_to_df(merged_dict, files[file_name])
        #add left over empty pud and tid loop that cannot be got from any other objs    
        if not_created_pid_tid_pairs:
            for pid, tid in not_created_pid_tid_pairs:
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
                files[file].head(0).to_csv(file_path, sep=';', index=False)
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
        expert_df['Speedup if no scalar integer'] = expert_df['CQA cycles'] / expert_df['CQA cycles if no scalar integer'] 
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
            file_name = '{}_{}_{}_cqa.csv'.format(cqa.fk_decan_variant_id, module_name, cqa.loop.maqao_loop_id) if \
                    cqa.fk_decan_variant_id is not None else '{}_{}_cqa.csv'.format(module_name, cqa.loop.maqao_loop_id)
            cqa_path = os.path.join(cqa_dir_path, file_name)

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
        asm_dir_path = self.get_asm_path()
        os.makedirs(asm_dir_path, exist_ok=True)

        for asm in asm_collection.get_objs():

            #check if asm is function or loop
            if asm.loops: 

                module_name = os.path.basename(asm.loops[0].function.module.name)

                content = asm.content
                file_name = '{}_{}.csv'.format(module_name, asm.loops[0].maqao_loop_id)
                path = os.path.join(asm_dir_path, file_name)
                with open(path, 'wb') as f:
                    f.write(decompress_file(content))
            else:
                module_name = os.path.basename(asm.functions[0].module.name)
                content = asm.content
                file_name = 'fct_{}_{}.csv'.format(module_name, asm.functions[0].maqao_function_id)
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
                file_name = '{}_{}.csv'.format(module_name, loop.maqao_loop_id)
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
                files[file_name] = pd.DataFrame()

            files[file_name] = files[file_name].append(group_dict,ignore_index=True)
            
        for file in files:
            write_file(files[file],os.path.join(group_dir_path, file))

            
            
