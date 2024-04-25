import pandas as pd
from sqlalchemy import (
    Table,
    create_engine,
    Column,
    Integer,
    BigInteger,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    PickleType,
    JSON,
    LargeBinary
)
import sqlalchemy
import hashlib
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship,registry
import inspect
from pickle import dumps, loads
from gzip import zlib
import os
import math

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import subprocess
Base = declarative_base()
def is_nan(value):
    return isinstance(value, float) and math.isnan(value)
class QaaSBase(Base):
    __abstract__ = True
    def __init__(self, session=None):
        super().__init__()
        if session is not None:
            session.add(self)

    table_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

class FileBlobBase(QaaSBase):
    __abstract__ = True
    def __init__(self, session=None):
        super().__init__(session)
    
    def dump_file(self, content, target_path):
        target_dir = os.path.dirname(target_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)  
        with open(target_path, 'wb') as f:
            f.write(content)

    def load_file(self, filename):
        with open(filename, 'rb') as f:
            content = f.read()
        return content
    
    def compress_file(self, file_path, large_file_folder, table_name, column_name, table_obj, session):
        #flush session to get table id
        session.flush()
        target_path = os.path.join(large_file_folder, table_name, column_name, str(table_obj.table_id))
        
        with open(file_path, 'rb') as f:
            content = f.read()
        compressed_content = zlib.compress(content, 9)
        self.dump_file(self, compressed_content, target_path)
        return target_path

    def decompress_file(self, filename):
        compressed_content = self.load_file(self, filename)
        return zlib.decompress(compressed_content)
    
    def get_file_sha256(self, filename):
        with open(filename, 'rb') as f:
            sha256_hash = hashlib.sha256(f.read()).hexdigest()
        return sha256_hash
   
            


class HashableQaaSBase(FileBlobBase):
    __abstract__ = True
    def __init__(self, session=None):
        super().__init__(session)
    
    @classmethod
    def files_are_identical(cls, file1, file2):
        """ check if two files have same content """
        try:
            result = subprocess.run(['diff', file1, file2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.stdout:
                return False
            return True
        except Exception as e:
            print(f"An error occurred while comparing files: {e}")
            return False
        
    @classmethod
    def find_identical_by_hash(cls, file_path, file_hash, session):
        """
        get results by using hash, then get the idetntical one if there is otherwise return None
        """
        results = session.query(cls).filter_by(hash=file_hash).all()
        for result in results:
            if cls.files_are_identical(result.content, file_path):
                return result
        return None

    @classmethod
    def get_or_create_obj_by_hash(cls, file_path, large_file_data_dir, table_name, initializer):
        hash = cls.get_file_sha256(file_path)
        identical_result = cls.find_identical_by_hash(file_path, hash, initializer.session)
        if identical_result:
            return identical_result
        else:
            new_obj = cls(initializer)
            #make sure we have a table id
            new_obj.hash = hash 
            new_obj.content = new_obj.compress_file(file_path, large_file_data_dir, table_name, "content", new_obj, initializer.session)

            return new_obj


mapper_registry = registry()

class CompressedPickler(object):
    @classmethod
    def dumps(cls, obj, protocol=2):
        s = dumps(obj, protocol)
        sz = zlib.compress(s, 9)
        if len(sz) < len(s):
            return sz
        else:
            return s

    @classmethod
    def loads(cls, string):
        try:
            s = zlib.decompress(string)
        except:
            s = string
        return loads(s)


class Application(QaaSBase):
    __tablename__ = "application"
    workload = Column(Text, nullable=True)
    version = Column(Text, nullable=True)
    program = Column(Text, nullable=True)
    commit_id = Column(Text, nullable=True)
    #TODO
    mpi_scaling = Column(Text, nullable = True)
    omp_scaling = Column(Text, nullable = True)
    executions = relationship("Execution", back_populates="application")
    def __init__(self, initializer):
        super().__init__(initializer.session)
  
        self.accept(initializer)
        
    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitApplication(self)

    @classmethod
    def get_or_create_application(cls, workload, version, program, commit_id, initializer):
        result = initializer.session.query(cls).filter_by(workload = workload, version = version, program = program, commit_id = commit_id).first()
        if result:
            return result
        else:
            new_os_obj = cls(initializer)
            new_os_obj.workload = workload 
            new_os_obj.version = version 
            new_os_obj.program = program 
            new_os_obj.commit_id = commit_id 

            return new_os_obj
        
class Execution(FileBlobBase):
    __tablename__ = "execution"
    is_src_code = Column(Boolean, nullable = True)
    universal_timestamp = Column(String(50), nullable = True)
    #from expert runs
    time= Column(Float, nullable = True)
    profiled_time = Column(Float, nullable = True)
    max_nb_threads = Column(Integer, nullable = True)
    #logs
    #print(LONGBLOB)
    #print(LargeBinary().with_variant(LONGBLOB,"mysql", "mariadb"))
    log = Column(Text, nullable = True)
    lprof_log = Column(Text, nullable = True)
    # log = Column(LONGBLOB, nullable = True)
    # lprof_log = Column(LONGBLOB, nullable = True)
    cqa_context = Column(JSON, nullable = True)
    config = Column(JSON, nullable = True)
    global_metrics = Column(JSON, nullable = True)
    #added column by qaas
    qaas_timestamp = Column(String(50))
    is_orig = Column(Boolean)
    #source location path
    loop_location = Column(JSON, nullable = True)
    fct_location = Column(JSON, nullable = True)
    loop_callchain = Column(JSON, nullable = True)
    fct_callchain = Column(JSON, nullable = True)
    threads_per_core = Column(Integer, nullable = True)
    #TODO add these 3 columns to the correct place put the three columns in the config in execution
    # MPI_threads = Column(Integer, nullable = True)
    # OMP_threads = Column(Integer, nullable = True)
    # affinity = Column(Text, nullable = True)

    fk_hwsystem_id = Column(Integer, ForeignKey('hwsystem.table_id'))
    fk_os_id = Column(Integer, ForeignKey('os.table_id'))
    fk_application_id = Column(Integer, ForeignKey('application.table_id')) 
    fk_compiler_option_id = Column(Integer, ForeignKey('compiler_option.table_id'))

    lprof_categorizations  = relationship("LprofCategorization", back_populates="execution")
    src_functions  = relationship("SrcFunction", back_populates="execution")
    modules  = relationship("Module", back_populates="execution")
    blocks  = relationship("Block", back_populates="execution")
    src_loops = relationship("SrcLoop", back_populates="execution")
    qaass = relationship("QaaS", back_populates="orig_execution")
    qaas_runs = relationship("QaaSRun", back_populates="execution")
    maqaos = relationship("Maqao", back_populates="execution")
    compiler_reports = relationship("CompilerReport", back_populates="execution")

    os = relationship("Os", back_populates="executions")
    hwsystem = relationship("HwSystem", back_populates="executions")
    application = relationship("Application", back_populates="executions")
    compiler_option = relationship("CompilerOption", back_populates="executions")

    def __init__(self, initializer):
        super().__init__(initializer.session)
        self.accept(initializer)
    
    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitExecution(self)

    def add_src_loop_if_not_exist(self, new_src_loop):
        for existing_src_loop in self.src_loops:
            if existing_src_loop == new_src_loop: 
                print("create new loop does not exist in current arrays")
                return  
        self.src_loops.append(new_src_loop)

    @classmethod
    def get_obj(cls, timestamp, session):
        result = session.query(cls).filter_by(universal_timestamp=timestamp).first()
        if result:
            return result
        else:
            return None


class QaaS(QaaSBase):
    __tablename__ = "qaas"
    timestamp = Column(Text, nullable = True)

    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    orig_execution  = relationship("Execution", back_populates="qaass")

    qaas_runs = relationship("QaaSRun", back_populates="qaas")
   

    def __init__(self, initializer):
        super().__init__(initializer.session)
        self.accept(initializer)


    def accept(self, accessor):
        accessor.visitQaaS(self)

    @classmethod
    def get_or_create_qaas(cls, timestamp, initializer):
        result = initializer.session.query(cls).filter_by(timestamp = timestamp).first()
        if result:
            return result
        else:
            new_obj = cls(initializer)
            new_obj.timestamp = timestamp 
            return new_obj

class QaaSRun(QaaSBase):
    __tablename__ = "qaas_run"
    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    fk_qaas_id = Column(Integer, ForeignKey('qaas.table_id'))
    type = Column(Text, nullable = True)
    is_baseline = Column(Integer, nullable = True)


    execution  = relationship("Execution", back_populates="qaas_runs")
    qaas  = relationship("QaaS", back_populates="qaas_runs")

    def __init__(self, initializer):
        super().__init__(initializer.session)
    


#used to store all string that is ref by binary file index
class StringClass(QaaSBase):
    __tablename__ = "string"
    string = Column(Text, nullable = True)
    def __init__(self, session):
        super().__init__(session)

    @classmethod
    def get_or_create_table_id_by_string(cls, string, session):
        result = session.query(cls).filter_by(string=string).first()
        if result:
            return result.table_id
        else:
            new_string_obj = cls(session)
            new_string_obj.string = string
            return new_string_obj.table_id
    @classmethod
    def get_string_by_id(cls, id, session):
        result = session.query(cls).filter_by(table_id=id).one()
        if result:
            return result
        else:
            return None

class Os(QaaSBase):
    __tablename__ = "os"
    os_version = Column(Text, nullable = True)
    hostname = Column(String(50), nullable = True)
    scaling_governor = Column(Text, nullable = True)
    

    huge_pages = Column(Text, nullable = True)
    driver_frequency = Column(Text, nullable = True)
    fk_environment_id = Column(Integer, ForeignKey('environment.table_id'))

    executions  = relationship("Execution", back_populates="os")
    environment = relationship("Environment", back_populates="oss")
    def __init__(self, initializer):
        super().__init__(initializer.session)
        self.accept(initializer)
        
    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitOs(self)

    @classmethod
    def get_or_create_os_by_os_info(cls, hostname, initializer, os_version=None, scaling_governor=None, huge_pages=None, driver_frequency=None):
        result = initializer.session.query(cls).filter_by(hostname = hostname, os_version = os_version, scaling_governor = scaling_governor, huge_pages = huge_pages, driver_frequency = driver_frequency).first()
        if result:
            return result
        else:
            new_os_obj = cls(initializer)
            new_os_obj.hostname = hostname 
            new_os_obj.os_version = os_version
            new_os_obj.scaling_governor = scaling_governor
            new_os_obj.huge_pages = huge_pages
            new_os_obj.driver_frequency = driver_frequency

            return new_os_obj
  
class HwSystem(QaaSBase):
    __tablename__ = "hwsystem"
    cpui_model_name = Column(String(50), nullable = True)
    cpui_cpu_cores = Column(Integer, nullable = True)
    cpui_cache_size = Column(String(50), nullable = True)
    cur_frequency = Column(Integer, nullable = True)
    max_frequency = Column(Integer, nullable = True)
    min_frequency = Column(Integer, nullable = True)
    architecture = Column(String(50), nullable = True)
    uarchitecture = Column(String(50), nullable = True)
    proc_name = Column(String(50), nullable = True)
    hw_name = Column(String(50), nullable = True)
    memory = Column(String(50), nullable = True)
    sockets = Column(Integer, nullable = True)
    cores_per_socket = Column(Integer, nullable = True)
    executions  = relationship("Execution", back_populates="hwsystem")

    def __init__(self, initializer):
        super().__init__(initializer.session)
        self.accept(initializer)

    @classmethod
    def get_or_set_hwsystem(cls, cpui_model_name, architecture, uarchitecture, hwsystem, initializer):
        result = initializer.session.query(cls).filter_by(cpui_model_name = cpui_model_name, architecture = architecture, uarchitecture = uarchitecture).first()
        if result:
            return result
        else:
            hwsystem.cpui_model_name = cpui_model_name 
            hwsystem.architecture = architecture 
            hwsystem.uarchitecture = uarchitecture 
            return hwsystem
    
    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitHwSystem(self)

    
   
class Maqao(QaaSBase):
    __tablename__ = "maqao"
    global_instances_per_bucket = Column(Integer, nullable = True)
    instances_per_bucket = Column(Integer, nullable = True)
    architecture_code = Column(Integer, nullable = True)
    uarchitecture_code = Column(Integer, nullable = True)
    min_time_obj = Column(Float, nullable = True)
    cqa_uarch = Column(String(50), nullable = True)
    cqa_arch = Column(String(50), nullable = True)
    lprof_suffix = Column(String(50), nullable = True)
    last_html_path = Column(Text, nullable = True)
    maqao_build = Column(Text, nullable = True)
    maqao_version = Column(String(50), nullable = True)
    exp_version = Column(String(50), nullable = True)
    nb_filtered_functions = Column(Integer, nullable = True)
    cov_filtered_loops = Column(Integer, nullable = True)
    nb_filtered_loops = Column(Integer, nullable = True)
    config_count = Column(Integer, nullable = True)
    cov_filtered_functions = Column(Integer, nullable = True)


    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    
    execution  = relationship("Execution", back_populates="maqaos")
    def __init__(self, initializer):
        super().__init__(initializer.session)
        self.accept(initializer)

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitMaqao(self)
  
class Environment(QaaSBase):
    __tablename__ = "environment"

    environment_metrics = relationship("EnvironmentMetric", back_populates="environment")
    oss = relationship("Os", back_populates="environment")
    qaas_data_dir = None

    def __init__(self,  initializer):
        super().__init__(initializer.session)
        self.accept(initializer)

    def export(self, exporter):
        self.accept(exporter)

    def accept(self, accessor):
        accessor.visitEnvironment(self)

  
    def add_metrics(self, session, dic):
        metrics = []
        for metric_name, metric_value in dic.items():
            metric = EnvironmentMetric(session)
            metric.metric_name = metric_name
            metric.metric_value = metric_value
            metrics.append(metric)
        self.environment_metrics = metrics
        return metrics


class EnvironmentMetric(QaaSBase):
    __tablename__ = "environment_metric"
    metric_name = Column(String(50), nullable = True)
    metric_value = Column(Text, nullable = True)

    fk_environment_id = Column(Integer, ForeignKey('environment.table_id'))

    environment = relationship("Environment", back_populates="environment_metrics")

class Compiler(QaaSBase):
    __tablename__ = "compiler"
    vendor = Column(Text, nullable = True)
    version = Column(String(50), nullable = True)
    release_date = Column(DateTime, nullable = True)

    compiler_options  = relationship("CompilerOption", back_populates="compiler")

    def __init__(self, initializer):
        super().__init__(initializer.session)

    @classmethod
    def get_or_create_compiler_by_compiler_info(cls, vendor, version, initializer, release_date = None):
        result = initializer.session.query(cls).filter_by(vendor = vendor, version = version, release_date = release_date).first()
        if result:
            return result
        else:
            new_obj = cls(initializer)
            new_obj.vendor = vendor 
            new_obj.version = version 
            new_obj.release_date = release_date 
            return new_obj
    @classmethod
    def get_compiler_info(cls, vendor, version, initializer):
        result = initializer.session.query(cls).filter_by(vendor = vendor, version = version).first()
        return result

class CompilerReport(QaaSBase):
    __tablename__ = "compiler_report"
    content = Column(Text, nullable = True)
    # content = Column(LONGBLOB, nullable = True)

    hash = Column(String(64), nullable = True)
    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    execution  = relationship("Execution", back_populates="compiler_reports")

    def __init__(self, initializer):
        super().__init__(initializer.session)

    
class CompilerOption(QaaSBase):
    __tablename__ = "compiler_option"
    flag = Column(Text, nullable = True)
    fk_compiler_id = Column(Integer, ForeignKey('compiler.table_id'))
    compiler  = relationship("Compiler", back_populates="compiler_options")

    functions  = relationship("Function", back_populates="compiler_option")
    loops  = relationship("Loop", back_populates="compiler_option")
    modules  = relationship("Module", back_populates="compiler_option")
    blocks  = relationship("Block", back_populates="compiler_option")
    executions  = relationship("Execution", back_populates="compiler_option")

    def __init__(self, initializer):
        super().__init__(initializer.session)
    @classmethod
    def get_or_create_compiler_option(cls, flag, initializer):
        result = initializer.session.query(cls).filter_by(flag = flag).first()
        if result:
            return result
        else:
            new_obj = cls(initializer)
            new_obj.flag = flag 
            return new_obj
        
class LprofCategorization(QaaSBase):
    __tablename__ = "lprof_categorization"
    node = Column(String(50), nullable = True, name ="Node")
    process = Column(String(50), nullable = True, name ="Process")
    thread = Column(String(50), nullable = True, name ="Thread")
    nb_cycle_events = Column(Integer, nullable = True,name="Nb Cycle Events")
    time_s = Column(Float, nullable = True,name = "Time (s)")
    
    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))

    lprof_categorization_metrics  = relationship("LprofCategorizationMetric", back_populates="lprof_categorization",collection_class=list)
    execution  = relationship("Execution", back_populates="lprof_categorizations")
    
    def __init__(self, initializer):
        super().__init__(initializer.session)

    def add_metrics(self, session, dic):
        metrics = []
        for metric_name, metric_value in dic.items():
            metric = LprofCategorizationMetric(session)
            metric.metric_name = metric_name
            metric.metric_value =  metric_value
            metrics.append(metric)
        self.lprof_categorization_metrics = metrics
        return metrics
    
    

class LprofCategorizationMetric(QaaSBase):
    __tablename__ = "lprof_categorization_metric"
    metric_name = Column(String(50), nullable = True)
    metric_value = Column(Text, nullable = True)

    fk_lprof_categorization_id = Column(Integer, ForeignKey('lprof_categorization.table_id'))

    lprof_categorization  = relationship("LprofCategorization", back_populates="lprof_categorization_metrics")
    def __init__(self, session):
        super().__init__(session)

class Module(QaaSBase):
    __tablename__ = "module"
    name = Column(Text, nullable=True)
    time_p = Column(Float, nullable = True)
    time_s = Column(Float, nullable = True)
    cpi_ratio = Column(Float, nullable = True)

    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    fk_compiler_option_id = Column(Integer, ForeignKey('compiler_option.table_id'))

    functions = relationship("Function", back_populates="module")
    blocks = relationship("Block", back_populates="module")
    execution  = relationship("Execution", back_populates="modules")
    compiler_option = relationship("CompilerOption", back_populates="modules")
    def __init__(self, initializer):
        super().__init__(initializer.session)

    @classmethod
    def get_or_create_by_name(cls, name, current_execution, initializer):
        result = initializer.session.query(cls).filter(cls.name.like('%'+name), cls.execution == current_execution).first()
        if result:
            return result
        else:
            new_obj = cls(initializer)
            new_obj.name = name
            new_obj.execution = current_execution
            return new_obj
    
class Block(QaaSBase):
    __tablename__ = "block"
    maqao_block_id = Column(Integer, nullable = True)
    file = Column(Text, nullable=True)
    line_number = Column(Text, nullable = True)
    pid = Column(Integer, nullable=True)
    tid = Column(Integer, nullable=True)

    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    fk_module_id = Column(Integer, ForeignKey('module.table_id'))
    fk_compiler_option_id = Column(Integer, ForeignKey('compiler_option.table_id'))

    execution  = relationship("Execution", back_populates="blocks")
    lprof_measurements  = relationship("LprofMeasurement", back_populates="block")
    module = relationship("Module", back_populates="blocks")
    compiler_option = relationship("CompilerOption", back_populates="blocks")


    def __init__(self, initializer):
        super().__init__(initializer.session)

class Function(QaaSBase):
    __tablename__ = "function"
    function_name = Column(Text, nullable = True)
    label_name = Column(Text, nullable = True)
    maqao_function_id = Column(Integer, nullable = True)
    cats = Column(Text, nullable = True)
    pid = Column(Integer, nullable=True)
    tid = Column(Integer, nullable=True)
    hierarchy = Column(JSON, nullable = True)
    fk_module_id = Column(Integer, ForeignKey('module.table_id'))
    fk_compiler_option_id = Column(Integer, ForeignKey('compiler_option.table_id'))
    fk_src_function_id = Column(Integer, ForeignKey('src_function.table_id'))

    loops = relationship("Loop", back_populates="function")
    asms  = relationship("Asm", back_populates="function")
    module  = relationship("Module", back_populates="functions")
    lprof_measurements  = relationship("LprofMeasurement", back_populates="function")
    compiler_option = relationship("CompilerOption", back_populates="functions")
    src_function = relationship("SrcFunction", back_populates="functions")
    cqa_measures = relationship("CqaMeasure", back_populates="function")
    def __init__(self, initializer):
        super().__init__(initializer.session)


    @classmethod
    def get_or_create_function_by_function_name(cls, function_name, initializer):
        result = initializer.session.query(cls).filter_by(function_name=function_name).first()
        if result:
            return result
        else:
            new_function_obj = cls(initializer)
            new_function_obj.function_name = function_name
            return new_function_obj
        
class SrcFunction(QaaSBase):
    __tablename__ = "src_function"
    file = Column(Text, nullable = True)
    line_number = Column(Text, nullable = True)

    fk_source_id = Column(Integer, ForeignKey('source.table_id'))
    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))

    source  = relationship("Source", back_populates="src_functions")
    execution  = relationship("Execution", back_populates="src_functions")
    functions = relationship("Function", back_populates="src_function")
    def __init__(self, initializer):
        super().__init__(initializer.session)

class Loop(QaaSBase):
    __tablename__ = "loop"
    maqao_loop_id = Column(Integer, nullable = True)
    level = Column(Integer, nullable = True)
    pid = Column(Integer, nullable=True)
    tid = Column(Integer, nullable=True)
    # run_type = Column(Integer, nullable = True)

    fk_function_id = Column(Integer,ForeignKey('function.table_id'))
    fk_src_loop_id = Column(Integer, ForeignKey('src_loop.table_id'))
    fk_compiler_option_id = Column(Integer, ForeignKey('compiler_option.table_id'))

    function  = relationship("Function", back_populates="loops")
    src_loop  = relationship("SrcLoop", back_populates="loops")
    compiler_option = relationship("CompilerOption", back_populates="loops")
    lprof_measurements  = relationship("LprofMeasurement", back_populates="loop")
    groups = relationship("Group", back_populates="loop")
    cqa_measures = relationship("CqaMeasure", back_populates="loop")
    lore_loop_measures = relationship("LoreLoopMeasure", back_populates="loop")
    vprof_measures = relationship("VprofMeasure", back_populates="loop")
    decan_runs = relationship("DecanRun", back_populates="loop")
    asms  = relationship("Asm", back_populates="loop")

    def __init__(self, initializer):
        super().__init__(initializer.session)
class SrcLoop(QaaSBase):
    __tablename__ = "src_loop"
    file = Column(Text, nullable=True)
    line_number = Column(Text, nullable = True)
    mutation_number = Column(Integer, nullable = True)

    fk_source_id = Column(Integer, ForeignKey('source.table_id'))
    fk_execution_id = Column(Integer, ForeignKey('execution.table_id'))
    fk_mutation_id = Column(Integer, ForeignKey('mutation.table_id'))
    #self referiental
    fk_orig_src_loop_id = Column(Integer, ForeignKey('src_loop.table_id'), nullable=True)

    loops = relationship("Loop", back_populates="src_loop")
    source = relationship("Source", back_populates="src_loops")
    execution  = relationship("Execution", back_populates="src_loops")
    mutation = relationship("Mutation", back_populates="src_loops")
    #self referiental
    orig_src_loop = relationship("SrcLoop", remote_side='SrcLoop.table_id')

    def __init__(self, initializer):
        super().__init__(initializer.session)

    @classmethod
    def get_src_loop_by_id(cls, initializer, id):
        try:
            res = initializer.session.query(SrcLoop).filter_by(table_id=id).one()
            return res
        except (NoResultFound, MultipleResultsFound):
            return None
        


   
class LoreLoopMeasure(QaaSBase):
    __tablename__ = "lore_loop_measure"
    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))

    loop = relationship("Loop", back_populates="lore_loop_measures")
    lore_loop_measure_metrics  = relationship("LoreLoopMeasureMetric", back_populates="lore_loop_measure")
    def __init__(self, initializer):
        super().__init__(initializer.session)
   
    def add_metrics(self, session, dic):
        metrics = []
        for metric_name, metric_value in dic.items():
            metric = LoreLoopMeasureMetric(session)
            metric.metric_name = metric_name
            metric.metric_value = metric_value
            metrics.append(metric)

        self.lore_loop_measure_metrics = metrics
        return metrics
class LoreLoopMeasureMetric(QaaSBase):
    __tablename__ = "lore_loop_measure_metrics"
    metric_name = Column(String(50), nullable = True)
    metric_value = Column(Text, nullable = True)
    fk_lore_loop_measure_id = Column(Integer, ForeignKey('lore_loop_measure.table_id'))

    lore_loop_measure  = relationship("LoreLoopMeasure", back_populates="lore_loop_measure_metrics")

    def __init__(self, session):
        super().__init__(session)


class LprofMeasurement(QaaSBase):
    __tablename__ = "lprof_measurement"
    time_p = Column(Float, nullable = True)
    time_s = Column(Float, nullable = True)
    time_s_min = Column(Float, nullable = True)
    time_s_max = Column(Float, nullable = True)
    time_s_avg = Column(Float, nullable = True)
    cov_deviation = Column(Float, nullable = True)
    time_deviation = Column(Float, nullable = True)
    nb_threads = Column(Integer, nullable = True)

    fk_function_id = Column(Integer, ForeignKey('function.table_id'))
    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))
    fk_block_id = Column(Integer, ForeignKey('block.table_id'))

    function  = relationship("Function", back_populates="lprof_measurements")
    loop  = relationship("Loop", back_populates="lprof_measurements")
    block  = relationship("Block", back_populates="lprof_measurements")
    
    def __init__(self, initializer):
        super().__init__(initializer.session)
    @classmethod
    def get_obj_info(cls, session, obj, obj_col_name):
        try:
            session.flush()
            res = session.query(LprofMeasurement).filter(getattr(LprofMeasurement, obj_col_name) == obj).one()
            return res
        except sqlalchemy.orm.exc.NoResultFound:
            return None
    
        

  



class Mutation(QaaSBase):
    __tablename__ = "mutation"
    pluto = Column(Integer, nullable = True)
    interchange_order = Column(Integer, nullable = True)
    interchange_arg = Column(Text, nullable = True)
    tiling_order = Column(Integer, nullable = True)
    tiling_arg = Column(Text, nullable = True)
    unrolling_order = Column(Integer, nullable = True)
    unrolling_arg = Column(Text, nullable = True)
    distribution_order = Column(Integer, nullable = True)
    distribution_arg = Column(Text, nullable = True)
    unrolljam_order = Column(Integer, nullable = True)
    unrolljam_arg = Column(Text, nullable = True)
    valid = Column(Integer, nullable = True)

    src_loops = relationship("SrcLoop", back_populates="mutation")
    def __init__(self, initializer):
        super().__init__(initializer.session)

    @classmethod
    def get_or_create_mutation_by_mutation_info(cls, mutation_info, initializer):
        mutation = initializer.session.query(cls).filter_by(
            pluto=mutation_info.get('pluto', None),
            interchange_order=mutation_info.get('interchange_order', None),
            interchange_arg=mutation_info.get('interchange_arg', None),
            tiling_order=mutation_info.get('tiling_order', None),
            tiling_arg=mutation_info.get('tiling_arg', None),
            unrolling_order=mutation_info.get('unrolling_order', None),
            unrolling_arg=mutation_info.get('unrolling_arg', None),
            distribution_order=mutation_info.get('distribution_order', None),
            distribution_arg=mutation_info.get('distribution_arg', None),
            unrolljam_order=mutation_info.get('unrolljam_order', None),
            unrolljam_arg=mutation_info.get('unrolljam_arg', None),
            valid=mutation_info.get('valid', None)
        ).first()
        if not mutation:
            mutation = cls(initializer)
            for field, value in mutation_info.items():
                if hasattr(mutation, field):
                    setattr(mutation, field, value)
        return mutation


class CqaMeasure(QaaSBase):
    __tablename__ = "cqa_measure"
    path_id = Column(Integer, nullable = True)

    fk_decan_variant_id = Column(Integer, ForeignKey('decan_variant.table_id'))
    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))
    fk_function_id = Column(Integer, ForeignKey('function.table_id'))
    fk_analysis_id = Column(Integer, ForeignKey('cqa_analysis.table_id'))

    cqa_metrics  = relationship("CqaMetric", back_populates="cqa_measure")
    loop  = relationship("Loop", back_populates="cqa_measures")
    function  = relationship("Function", back_populates="cqa_measures")
    decan_variant = relationship("DecanVariant", back_populates="cqa_measures")
    cqa_analysis = relationship("CqaAnalysis", back_populates="cqa_measures")

    def __init__(self, initializer):
        super().__init__(initializer.session)
   
    def add_metrics(self, session, dic):
        metrics = []
        for metric_name, metric_value in dic.items():
            metric = CqaMetric(session)
            metric.metric_name = metric_name
            metric.metric_value = metric_value
            metrics.append(metric)
        self.cqa_metrics = metrics
        return metrics

    def lookup_metric(self, name):
        return [float(m.metric_value) if m.metric_value != "NA" else None for m in self.cqa_metrics if m.metric_name == name]


    def lookup_metric_unique(self, name):
        rst = self.lookup_metric(name)
        #metric does not exist
        if len(rst) == 0: return None
        #should not return multiple
        assert len(rst) == 1
        return rst[0]
    
    


class CqaAnalysis(QaaSBase):
    __tablename__ = "cqa_analysis"
    analysis = Column(JSON, nullable = True)

    cqa_measures = relationship("CqaMeasure", back_populates="cqa_analysis")

    @classmethod
    def add_analysis(cls, session, analysis_json):
        cqa_analysis = CqaAnalysis(session)
        cqa_analysis.analysis = analysis_json
        return cqa_analysis
    def __init__(self, session):
        super().__init__(session)

class CqaMetric(QaaSBase):
    __tablename__ = "cqa_metric"
    metric_name = Column(Text, nullable = True)
    metric_value = Column(Text, nullable = True)

    fk_cqa_measure_id = Column(Integer, ForeignKey('cqa_measure.table_id'))

    cqa_measure  = relationship("CqaMeasure", back_populates="cqa_metrics")

    def __init__(self, session):
        super().__init__(session)


class Asm(HashableQaaSBase):
    __tablename__ = "asm"
    content = Column(Text, nullable = True)
    # content = Column(LONGBLOB, nullable = True)
    hash = Column(String(64), nullable = True)
    fk_decan_variant_id = Column(Integer, ForeignKey('decan_variant.table_id'))
    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))
    fk_function_id = Column(Integer, ForeignKey('function.table_id'))

    decan_variant = relationship("DecanVariant", back_populates="asms")
    function = relationship("Function", back_populates="asms")
    loop = relationship("Loop", back_populates="asms")

    def __init__(self, initializer):
        super().__init__(initializer.session)
    
    @classmethod
    def get_or_create_asm_by_hash(cls, file_path, large_file_data_dir, initializer):
        cls.get_or_create_obj_by_hash(cls, file_path, large_file_data_dir, "asm", initializer)

class Source(HashableQaaSBase):
    __tablename__ = "source"
    content = Column(Text, nullable = True)
    # content = Column(LONGBLOB, nullable = True)

    hash = Column(String(64), nullable = True)

    src_functions = relationship("SrcFunction", back_populates="source")
    src_loops = relationship("SrcLoop", back_populates="source")
    source_metrics = relationship("SourceMetric", back_populates="source")

    def __init__(self, initializer):
        super().__init__(initializer.session)

    def add_metrics(self, session, dic):
        metrics = []
        for metric_name, metric_value in dic.items():
            metric = SourceMetric(session)
            metric.metric_name = metric_name
            metric.metric_value = metric_value
            metrics.append(metric)
        self.source_metrics = metrics
        return metrics


    @classmethod
    def get_or_create_source_by_hash(cls, file_path, source_metrics, large_file_data_dir, initializer):
        result = cls.get_or_create_obj_by_hash(cls, file_path, large_file_data_dir, "source", initializer)
        if source_metrics and len(result.source_metics) == 0:
            result.add_metrics(initializer.session, source_metrics)
        return result


class SourceMetric(QaaSBase):
    __tablename__ = "source_metrics"
    metric_name = Column(Text, nullable = True)
    metric_value = Column(Text, nullable = True)

    fk_source_id = Column(Integer, ForeignKey('source.table_id'))

    source = relationship("Source", back_populates="source_metrics")



class Group(QaaSBase):
    __tablename__ = "group"
    group_size = Column(Integer, nullable = True)
    pattern = Column(Text, nullable = True)
    opcodes = Column(Text, nullable = True)
    offsets = Column(Text, nullable = True)
    addresses = Column(Text, nullable = True)
    stride_status = Column(String(50), nullable = True)
    stride = Column(Integer, nullable = True)
    memory_status = Column(String(50), nullable = True)
    accessed_memory = Column(Integer, nullable = True)
    accessed_memory_nooverlap = Column(Integer, nullable = True)
    accessed_memory_overlap = Column(Integer, nullable = True)
    span = Column(Integer, nullable = True)
    head = Column(Integer, nullable = True)
    unroll_factor = Column(Integer, nullable = True)

    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))


    loop = relationship("Loop", back_populates="groups")

    def __init__(self, initializer):
        super().__init__(initializer.session)

class DecanRun(QaaSBase):
    __tablename__ = "decan_run"
    maqao_decan_id = Column(Integer, nullable = True)
    type = Column(String(50), nullable = True)
    frequency = Column(Float, nullable = True)
    bucket = Column(Integer, nullable = True)
    mpi_process = Column(Text, nullable = True)
    thread = Column(Text, nullable = True)

    fk_variant_id = Column(Integer, ForeignKey('decan_variant.table_id'))
    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))

    decan_metrics = relationship("DecanMetric", back_populates="decan_run")
    decan_variant = relationship("DecanVariant", back_populates="decan_runs")
    loop = relationship("Loop", back_populates="decan_runs")

    def __init__(self, initializer):
        super().__init__(initializer.session)

    def add_metric(self, initializer, metric_name, metric_value, metric_type):
        metric = DecanMetric(initializer)
        metric.metric_name = metric_name
        metric.metric_value = metric_value
        metric.metric_type = metric_type
        self.decan_metrics.append(metric) 
        return metric


class DecanVariant(QaaSBase):
    __tablename__ = "decan_variant"
    variant_name = Column(String(50), nullable = True)

    decan_runs = relationship("DecanRun", back_populates="decan_variant")
    asms = relationship("Asm", back_populates="decan_variant")
    cqa_measures = relationship("CqaMeasure", back_populates="decan_variant")
    def __init__(self, initializer):
        super().__init__(initializer.session)

    @classmethod
    def get_or_create_by_name(cls, variant_name, initializer):
        if variant_name:
            result = initializer.session.query(cls).filter_by(variant_name=variant_name).first()
            if result:
                return result
            else:
                new_obj = cls(initializer)
                new_obj.variant_name = variant_name
                return new_obj

class DecanMetric(QaaSBase):
    __tablename__ = "decan_metric"
    metric_name = Column(String(50), nullable = True)
    metric_value = Column(Text, nullable = True)
    metric_type = Column(String(50), nullable = True)

    fk_decan_run_id = Column(Integer, ForeignKey('decan_run.table_id'))

    decan_run = relationship("DecanRun", back_populates="decan_metrics")
    def __init__(self, initializer):
        super().__init__(initializer.session)
    
    @classmethod
    def get_metric_by_decan(cls, decan_run, initializer):
        result = initializer.session.query(cls).filter_by(decan_run=decan_run).first()
        assert result is not None, "No matching record found for the provided decan_run."
        return result
        

class VprofMeasure(QaaSBase):
    __tablename__ = "vprof_measure"

    instance_count = Column(BigInteger, nullable=True)
    invalid_count = Column(Integer, nullable=True)
    iteration_total = Column(Float, nullable=True)
    iteration_min = Column(Float, nullable=True)
    iteration_max = Column(Float, nullable=True)
    iteration_mean = Column(Float, nullable=True)
    cycle_total = Column(Float, nullable=True)
    cycle_min = Column(Float, nullable=True)
    cycle_max = Column(Float, nullable=True)
    cycle_mean = Column(Float, nullable=True)
    cycles_per_iteration_min = Column(Float, nullable=True)
    cycles_per_iteration_max = Column(Float, nullable=True)
    cycles_per_iteration_mean = Column(Float, nullable=True)

    fk_loop_id = Column(Integer, ForeignKey('loop.table_id'))

    loop = relationship("Loop", back_populates="vprof_measures")
    
    vprof_bucket_measures = relationship("VprofBucketMeasure", back_populates="vprof_measure")

    def __init__(self, initializer):
        super().__init__(initializer.session)
class VprofBucketMeasure(QaaSBase):
    __tablename__ = "vprof_bucket_measure"

    range_value  = Column(Text, nullable=True)
    bucket_instance_percent = Column(Text, nullable=True)
    bucket_cycle_percent = Column(Text, nullable=True)
    bucket_instances = Column(Text, nullable=True)

    fk_vprof_measure = Column(Integer, ForeignKey('vprof_measure.table_id'))

    vprof_measure = relationship("VprofMeasure", back_populates="vprof_bucket_measures")
    def __init__(self, initializer):
        super().__init__(initializer.session)

def connect_db(url):
    engine = create_engine(url)
    create_all(engine)
    engine.connect()
    return engine

def create_all(engine):
    Base.metadata.create_all(engine)
    mapper_registry.configure()
    print("created all tables")
    return engine

def create_all_tables(url):
    engine = connect_db(url)
    return create_all(engine)
    

def bulk_insert_data(table, data, Session):
    session = Session()
    try:
        session.bulk_insert_mappings(table, data)
        session.commit()
        print('Data inserted successfully')
    except Exception as e:
        session.rollback()
        print(f'Error inserting data: {e}')
    finally:
        session.close()

#get all columns of a table except for the autoincremented id
def get_columns(table):
    return [column.name for column in table.__table__.columns if not column.primary_key and not column.foreign_keys]

def get_extra_columns(table):
    return [column.name for column in table.__table__.columns if column.primary_key or column.foreign_keys ]

def get_table_data_from_df(df, Table):
    return df.loc[:, get_columns(Table)].to_dict(orient='records')

def get_module_by_name(modules, module_name):
    return [m for m in modules if os.path.basename(m.name) == module_name][0]

def get_function_by_maqao_id_module(current_execution, maqao_id, module):
    res = None
    for src_function in current_execution.src_functions:
        for f in src_function.functions:
            if f.maqao_function_id == maqao_id and os.path.basename(f.module.name) == module:
                return f
    return res
def get_loop_by_maqao_id_module(current_execution, maqao_id, module):
    res = None
    for src_loop in current_execution.src_loops:
        for l in src_loop.loops:
            if l.maqao_loop_id == maqao_id and l.function and os.path.basename(l.function.module.name) == module:
                return l
    return res

def get_loop_by_maqao_id(current_execution, maqao_id):
    res = None
    for src_loop in current_execution.src_loops:
        for l in src_loop.loops:
            if l.maqao_loop_id == maqao_id and l.function:
                return l
    return res


