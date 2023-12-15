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

from model_collection import *
from util import *
class QaaSDatabase:
    def __init__(self):
        #put as parameter
        self.data_list = []

    @classmethod
    def find_database(cls, timestamp, session):
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
        

    def accept(self, accessor):
        accessor.visitQaaSDataBase(self)

    # # export
    def export(self, exporter):
        for data in self.data_list:
            data.accept(exporter)