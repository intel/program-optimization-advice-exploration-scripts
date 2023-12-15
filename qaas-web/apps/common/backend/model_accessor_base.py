from abc import ABC, abstractmethod


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

