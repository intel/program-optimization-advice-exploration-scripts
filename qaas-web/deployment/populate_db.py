import sys
import os
import subprocess
import argparse

# Define the argument parser
parser = argparse.ArgumentParser(description='Run QAAS Script with Parameters')
parser.add_argument('--data', type=str, required=True, help='Directory for the output')
parser.add_argument('--workload', type=str, required=True, help='Workload Name')
parser.add_argument('--version', type=str, required=True, help='Workload Version Name')
parser.add_argument('--program', type=str, required=True, help='Workload Program Name')
parser.add_argument('--commit_id', type=str, required=True, help='Workload Program Commit ID')

# Parse the arguments
args = parser.parse_args()

#deploymet dir
script_dir = os.path.dirname(os.path.realpath(__file__))
# Get the path of the Python executable in the venv
venv_python_path = os.path.join(script_dir, '..', 'backend', 'venv', 'bin', 'python3')
# Check if the current Python executable is not the one in the venv
if sys.executable != venv_python_path:
    # If not, rerun this script with the Python executable from the venv
    os.execl(venv_python_path, venv_python_path, *sys.argv)
    
print(sys.executable)
    
# Get the absolute path of the directory containing the qaas module
qaas_dir = os.path.join(script_dir, '..', '..', 'qaas-backplane', 'src')
print(qaas_dir)
# Add the directory to sys.path
sys.path.append(qaas_dir)
# Get the directory of the script
# Calculate the path to the backend directory
qaas_web_backend_dir = os.path.join(script_dir, '..', 'backend')
# Add the backend directory to sys.path
sys.path.append(qaas_web_backend_dir)

from ovdb import populate_database, export_data
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import qaas
from server import app 
import configparser

from server import update_html, run_comparison_report
from model import create_all_tables

CONFIG_PATH=os.path.join(script_dir, "..", "config", "qaas-web.conf")
#get the config
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
create_all_tables(config)

####change this to ideal dir
# output_ov_dir = "/localdisk/yue/container_test/oneview_results_1676803461"
output_ov_dir = args.data


qaas_timestamp = os.path.basename(output_ov_dir)
# workload_name = f"workload_name"
# workload_version_name = f"version_name"
# workload_program_name = f"test_program_name"
# workload_program_commit_id = f"test###id"
workload_name = args.workload
workload_version_name = args.version
workload_program_name = args.program
workload_program_commit_id = args.commit_id

populate_database(output_ov_dir, qaas_timestamp, workload_version_name, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)
# with app.app_context():
#     update_html(workload_version_name)