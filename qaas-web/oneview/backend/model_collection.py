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


class DecanCollection(Collection):
    def __init__(self, objs=None):
        super().__init__(objs)
    
    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitDecanCollection(self)

class VprofCollection(Collection):
    def __init__(self, objs=None):
        super().__init__(objs)
    
    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitVprofCollection(self)

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