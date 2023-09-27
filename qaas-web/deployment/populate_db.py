import sys
import os
import subprocess
import argparse
import configparser

script_dir = os.path.dirname(os.path.realpath(__file__))

qaas_dir = os.path.join(script_dir, '..', '..', 'qaas-backplane', 'src')
CONFIG_PATH=os.path.join(script_dir, "..", "config", "qaas-web.conf")
#get the config
config = configparser.ConfigParser()
config.read(CONFIG_PATH)
# Add the directory to sys.path
sys.path.append(qaas_dir)
# Get the directory of the script
# Calculate the path to the backend directory
qaas_web_backend_dir = os.path.join(script_dir, '..', '..','qaas-web','oneview','backend')
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
from model import create_all_tables

def read_from_folder(folder_path):
    
    def process_result(result_folder, version_prefix):
        result = os.path.basename(result_folder)
        if "oneview_results_" not in result:
            return
        full_version = f"{version_prefix}{result}"
        qaas_timestamp = result.split('_')[-1]
        print(f"result path: {result_folder}, timestamp: {qaas_timestamp}, workload: {workload}, version: {full_version}, program: {program}")
        populate_database(result_folder, qaas_timestamp, full_version, workload, full_version, program, "")

    for workload in os.listdir(folder_path):
        for program in os.listdir(os.path.join(folder_path, workload)):
            for version in os.listdir(os.path.join(folder_path, workload, program)):
                version_path = os.path.join(folder_path, workload, program, version)
                
                # directly under version (e.g., 'orig')
                for item in os.listdir(version_path):
                    if "oneview_results_" in item:
                        process_result(os.path.join(version_path, item), f"{version}/")
                
                # under sub-directories of version (e.g., 'unicore')
                for sub_version in os.listdir(version_path):
                    sub_version_path = os.path.join(version_path, sub_version)
                    for result in os.listdir(sub_version_path):
                        if "oneview_results_" in result:
                            version_prefix = f"{os.path.relpath(sub_version_path, os.path.join(folder_path, workload, program))}/"
                            process_result(os.path.join(sub_version_path, result), version_prefix)


def main():
    # Define the argument parser
    parser = argparse.ArgumentParser(description='Run QAAS Script with Parameters')
    parser.add_argument('--data', type=str, help='Directory for the output')
    parser.add_argument('--workload', type=str, help='Workload Name')
    parser.add_argument('--version', type=str, help='Workload Version Name')
    parser.add_argument('--program', type=str,  help='Workload Program Name')
    parser.add_argument('--commit_id', type=str, help='Workload Program Commit ID')
    parser.add_argument('--read_from_folder', type=str, help='Read from a folder instead of arguments')

    # Parse the arguments
    args = parser.parse_args()

    if args.read_from_folder:
        read_from_folder(args.read_from_folder)
    else:
        output_ov_dir = args.data
        qaas_timestamp = os.path.basename(output_ov_dir)
        workload_name = args.workload
        workload_version_name = args.version
        workload_program_name = args.program
        workload_program_commit_id = args.commit_id

        populate_database(output_ov_dir, qaas_timestamp, workload_version_name, workload_name, workload_version_name, workload_program_name, workload_program_commit_id)



if __name__ == "__main__":
    CONFIG_PATH=os.path.join(script_dir, "..", "config", "qaas-web.conf")
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    # Create all tables
    create_all_tables(config)
    if len(sys.argv) > 1:
        main()
    else:
         # Calculate the path to the backend directory
        qaas_web_backend_dir = os.path.join(script_dir, '..', '..','qaas-web','oneview','backend')
        # Add the backend directory to sys.path
        sys.path.append(qaas_web_backend_dir)

       