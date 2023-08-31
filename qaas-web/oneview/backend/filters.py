
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
        print(data, self.value)
        return self.apply_with_mode(lambda d: self.value in d, data)


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
