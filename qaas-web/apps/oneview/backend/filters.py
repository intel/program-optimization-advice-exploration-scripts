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

from qaas_database import QaaSDatabase
from model_collection import *
from model_accessor import MetricGetter
from constants import *
class FilterStrategy:
    def __init__(self, type, operator, value, mode):
        self.type = type
        self.operator = operator
        self.value = value
        self.mode = mode

    def apply(self, data):
        pass  
    def apply_with_mode(self, condition_func, data):
        #if data is a list of values
        if isinstance(data, list):
            if self.mode == 'all':
                return all(condition_func(d) for d in data)
            elif self.mode == 'any':
                return any(condition_func(d) for d in data)
            else:
                return False 
        #data is a value
        else:
            return condition_func(data)
    
class LessThanFilterStrategy(FilterStrategy):
    def apply(self, data):
        return self.apply_with_mode(lambda d: float(d) < float(self.value), data)


class GreaterThanFilterStrategy(FilterStrategy):
    def apply(self, data):
        return self.apply_with_mode(lambda d: float(d) > float(self.value), data)


class EqualToFilterStrategy(FilterStrategy):
    def apply(self, data):
        return self.apply_with_mode(lambda d: float(d) == float(self.value), data)


class LikeFilterStrategy(FilterStrategy):
    def apply(self, data):
        return self.apply_with_mode(lambda d: self.value in d, data)

class ISFilterStrategy(FilterStrategy):
    def apply(self, data):
        return self.apply_with_mode(lambda d: self.value == d, data)
    
class FilterContext:
    def __init__(self, filters_info, session):
        self.filters = [self.create_filter_strategy(f) for f in filters_info]
        self.session = session

    def create_filter_strategy(self, filter_info):
        value = filter_info['value']
        operator = filter_info['operator']
        type = filter_info['type']
        mode = filter_info['mode'] 

        if operator == 'less than':
            return LessThanFilterStrategy(type, operator, value, mode)
        elif operator == 'bigger than':
            return GreaterThanFilterStrategy(type, operator, value, mode)
        elif operator == 'equal to':
            return EqualToFilterStrategy(type, operator, value, mode)
        elif operator == 'like':
            return LikeFilterStrategy(type, operator, value, mode)
        elif operator == 'is':
            return ISFilterStrategy(type, operator, value, mode)
        else:
            raise ValueError(f'Invalid operator: {filter_info["operator"]}')


    def is_satisfied(self, execution, filter_strategy):

        if filter_strategy.type in CQA_LOOP_METRIC_TYPES:
            qaas_database = QaaSDatabase.find_database(execution.universal_timestamp, self.session)
            cqa_collection = qaas_database.get_data_from_data_list(CqaCollection)
            values = MetricGetter(self.session, filter_strategy.type, cqa_collection).get_value()       
        elif filter_strategy.type in EXECUTION_METRIC_TYPES:
            values = MetricGetter(self.session, filter_strategy.type, execution).get_value()
        else:
            values = None
        return filter_strategy.apply(values) if values and values != "Not Available" else False

    def apply_all_filters(self, executions):
        filtered_executions = []
        for execution in executions:
            if all(self.is_satisfied(execution, filter_strategy) for filter_strategy in self.filters):
                filtered_executions.append(execution)
        return filtered_executions
