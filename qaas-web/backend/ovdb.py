import os
from model import *
from util import *
from model_accessor import OneViewModelInitializer,OneViewModelExporter
from qaas_database import QaaSDatabase
import pickle


# populate database given the data in qaas data folder, gui timestamp is the timestamp for both opt and orig
def populate_database(qaas_data_dir, qaas_timestamp, version, 
                      workload_name, workload_version_name, workload_program_name, workload_program_commit_id):
    #connect db
    config = get_config()
    engine = connect_db(config)
    Session = sessionmaker(bind=engine)
    session = Session()

    
    #######################populate database tables######################
    initializer = OneViewModelInitializer(session, qaas_data_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
    
    qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
    os.makedirs(qaas_output_folder, exist_ok=True)

    qaas_database = QaaSDatabase()
    qaas_database.accept(initializer)

    timestamp = qaas_database.universal_timestamp
  
    # export_data(timestamp, qaas_output_folder, session)
        
    session.commit()
    session.close()

def export_data(timestamp, qaas_output_folder, session):
    qaas_database = QaaSDatabase.find_database(timestamp, session)
    exporter = OneViewModelExporter(session, qaas_output_folder)
    print("start export data")
    qaas_database.export(exporter)
    print("finish export data")


