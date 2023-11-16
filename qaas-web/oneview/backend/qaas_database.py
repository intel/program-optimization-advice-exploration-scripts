
from model_collection import *
from util import *
class QaaSDatabase:
    def __init__(self):
        #put as parameter
        self.data_list = []
        print("4database created")

    @classmethod
    def find_database(cls, timestamp, session):
        print("in find database")
        qaas_database = cls()
        current_execution = Execution.get_obj(timestamp, session)
        qaas_database.add_to_data_list(current_execution)
        qaas_database.add_to_data_list(current_execution.hwsystem)
        qaas_database.add_to_data_list(current_execution.os)
        qaas_database.add_to_data_list(current_execution.maqaos[0])
        qaas_database.add_to_data_list(current_execution.os.environment)
        qaas_database.add_to_data_list(LprofCategorizationCollection(current_execution.lprof_categorizations))

        current_modules = current_execution.modules
        current_module_collection = ModuleCollection(current_modules)
        qaas_database.add_to_data_list(current_module_collection)


        current_blocks = current_execution.blocks
        current_block_collection = BlockCollection(current_blocks)
        qaas_database.add_to_data_list(current_block_collection)

        current_functions = get_all_functions_for_run(current_modules)
        current_function_collection = FunctionCollection(current_functions)
        qaas_database.add_to_data_list(current_function_collection)

        current_loops = get_all_loops_for_run(current_functions)
        current_loop_collection = LoopCollection(current_loops)
        qaas_database.add_to_data_list(current_loop_collection)

        decan_runs = []
        for loop in current_loops:
            decan_runs.extend(loop.decan_runs)
        current_decan_collection = DecanCollection(decan_runs)
        qaas_database.add_to_data_list(current_decan_collection)

        vprof_measures = []
        for loop in current_loops:
            vprof_measures.extend(loop.vprof_measures)
        current_vprof_collection = VprofCollection(vprof_measures)
        qaas_database.add_to_data_list(current_vprof_collection)


        current_lprof_measurments = get_all_lprof_measure_for_run(current_blocks, current_functions, current_loops)
        qaas_database.add_to_data_list(LprofMeasurementCollection(current_block_collection, current_function_collection, current_loop_collection, current_lprof_measurments))
        
        current_cqas = get_all_cqa_for_run(current_functions, current_loops)
        qaas_database.add_to_data_list(CqaCollection(current_cqas))
        
        current_asms = get_all_asm_for_run(current_functions, current_loops)
        qaas_database.add_to_data_list(AsmCollection(current_asms))

        current_sources = get_all_source_for_run(current_execution)
        qaas_database.add_to_data_list(SourceCollection(current_sources))

        current_groups = get_all_groups_for_run(current_loops)
        qaas_database.add_to_data_list(GroupCollection(current_groups))

        return qaas_database


  
    def add_to_data_list(self,obj):
        self.data_list.append(obj)
        
    #get the obj or collection obj from data list
    def get_data_from_data_list(self,target_obj):
        for obj in self.data_list:
            if isinstance(obj, target_obj):
                return obj

    def accept(self, accessor):
        accessor.visitQaaSDataBase(self)

    # # export
    def export(self, exporter):
        for data in self.data_list:
            data.accept(exporter)