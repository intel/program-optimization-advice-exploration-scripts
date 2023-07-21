
from qaas_database import QaaSDatabase
from model_collection import *
from model_accessor import MetricGetter
class FilterStrategy:
    def __init__(self, type, operator, value):
        self.type = type
        self.operator = operator
        self.value = value

    def apply(self, data):
        pass  
    
class LessThanFilterStrategy(FilterStrategy):
    def apply(self, data):
        return all(float(d) < float(self.value) for d in data)

class GreaterThanFilterStrategy(FilterStrategy):
    def apply(self, data):
        return all(float(d) > float(self.value) for d in data)

class EqualToFilterStrategy(FilterStrategy):
    def apply(self, data):
        return all(float(d) == float(self.value) for d in data)


class FilterContext:
    def __init__(self, filters_info, session):
        self.filters = [self.create_filter_strategy(f) for f in filters_info]
        self.session = session

    def create_filter_strategy(self, filter_info):
        value = filter_info['value']
        operator = filter_info['operator']
        type = filter_info['type']

        if operator == 'less than':
            return LessThanFilterStrategy(type, operator, value)
        elif operator == 'bigger than':
            return GreaterThanFilterStrategy(type, operator, value)
        elif operator == 'equal to':
            return EqualToFilterStrategy(type, operator, value)
        else:
            raise ValueError(f'Invalid operator: {filter_info["operator"]}')


    def is_satisfied(self, execution, filter_strategy):
        metric_getter = MetricGetter(self.session, filter_strategy.type)
        qaas_database = QaaSDatabase.find_database(execution.universal_timestamp, self.session)

        if filter_strategy.type == 'vectorization ratio':
            cqa_collection = qaas_database.get_data_from_data_list(CqaCollection)
            values = metric_getter.get_value(cqa_collection)
        elif filter_strategy.type in ['total time', 'array efficiency']:
            values = metric_getter.get_value(execution)
        else:
            values = None
        return filter_strategy.apply(values) if values else False

    def apply_all_filters(self, executions):
        filtered_executions = []
        for execution in executions:
            if all(self.is_satisfied(execution, filter_strategy) for filter_strategy in self.filters):
                filtered_executions.append(execution)
        return filtered_executions
