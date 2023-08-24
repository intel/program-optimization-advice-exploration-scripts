from ovdb import populate_database, export_data
from lore_migrator import migrate_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
# Get the absolute path of the directory containing the qaas module
qaas_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'qaas-backplane', 'src'))

# Add the directory to sys.path
sys.path.append(qaas_dir)

# Now you can import the qaas module
import qaas
from server import app 
import configparser

from server import update_html, run_comparison_report

SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", "config", "qaas-web.conf")
#get the config
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
output_ov_dir = "/localdisk/yue/expR2"
# ov_output_dir = os.path.join(output_ov_dir,'oneview_runs')
qaas_timestamp = os.path.basename(output_ov_dir)



workload_name = f"workload_name"
workload_version_name = f"version_name"
workload_program_name = f"test_program_name"
workload_program_commit_id = f"test###id"
populate_database(output_ov_dir, qaas_timestamp, workload_version_name, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)

#test lore read
# migrate_database()
#test ov data read and write
# for version in ['opt','orig']:
#     ov_version_output_dir = os.path.join(ov_output_dir, version)
#     result_folders = os.listdir(ov_version_output_dir)
#     # Should have only one folder
#     assert len(result_folders) == 1
#     result_folder = result_folders[0]
#     current_ov_dir = os.path.join(ov_version_output_dir, result_folder)
#     qaas_timestamp = os.path.basename(output_ov_dir)
#     workload_name = f"workload_name_{version}"
#     workload_version_name = f"version_name({version})"
#     workload_program_name = f"test_program_name_{version}"
#     workload_program_commit_id = f"test###id_{version}"
#     populate_database(current_ov_dir, qaas_timestamp, version, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
#     with app.app_context():
#         update_html(version)
    
# run_comparison_report()

#test export data
# def connect_db(config):
#     engine = create_engine(config['web']['SQLALCHEMY_DATABASE_URI'])
#     engine.connect()
#     return engine
# engine = connect_db(config)
# Session = sessionmaker(bind=engine)
# session = Session()
# qaas_output_folder = os.path.join(config['web']['QAAS_OUTPUT_FOLDER'])
# export_data('1681964819', qaas_output_folder, session)
# session.close()