import os
from model import *
class Collection:
    def __init__(self, objs=None):
        if objs is None:
            objs = []
        self.objs = objs

    def get_objs(self):
        return self.objs
    
    def add_obj(self, obj):
        self.objs.append(obj)
    
    def add_obj_list(self, obj_list):
        self.objs.extend(obj_list)
class LprofCategorizationCollection(Collection):
    def __init__(self, objs=None):
        super().__init__(objs)
    
   
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitLprofCategorizationCollection(self)

  


class ModuleCollection(Collection):
    def __init__(self, objs=None):
        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitModuleCollection(self)

class BlockCollection(Collection):
    def __init__(self, objs=None):
        
        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitBlockCollection(self)


class FunctionCollection(Collection):
    def __init__(self, objs=None):
        
        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitFunctionCollection(self)


class LoopCollection(Collection):
    def __init__(self, objs=None):
        
        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitLoopCollection(self)

class LprofMeasurementCollection(Collection):
    def __init__(self, block_collection, function_collection, loop_collection, objs=None):
        
        self.block_collection = block_collection
        self.function_collection = function_collection
        self.loop_collection = loop_collection

        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitLprofMeasurementCollection(self)

class CqaCollection(Collection):
    def __init__(self, objs=None):
        

        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitCqaCollection(self)

class AsmCollection(Collection):
    def __init__(self, objs=None):
        

        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitAsmCollection(self)

class GroupCollection(Collection):
    def __init__(self, objs=None):
        

        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitGroupCollection(self)

class SourceCollection(Collection):
    def __init__(self, objs=None):
        
        super().__init__(objs)
        
        

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitSourceCollection(self)