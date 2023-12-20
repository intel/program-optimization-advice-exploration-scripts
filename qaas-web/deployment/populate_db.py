import sys
import os
import subprocess
import argparse
import configparser
script_dir = os.path.dirname(os.path.realpath(__file__))
qaas_web_dir = os.path.join(script_dir, '..',)
apps_dir = os.path.join(qaas_web_dir, "apps")
config_dir =  os.path.join(apps_dir, "config")
CONFIG_PATH = os.path.join(config_dir, "qaas-web.conf")

qaas_dir = os.path.join(qaas_web_dir, '..', 'qaas-backplane', 'src')
sys.path.append(qaas_dir)

ov_web_backend_dir = os.path.join(apps_dir, 'oneview', 'backend')
sys.path.append(ov_web_backend_dir)

qaas_web_backend_dir = os.path.join(apps_dir, 'qaas', 'backend')
sys.path.append(qaas_web_backend_dir)

qaas_web_backend_common_dir = os.path.join(apps_dir, 'common','backend')
sys.path.append(qaas_web_backend_common_dir)

from ovdb import populate_database, export_data
from base_util import *
from qaasdb import populate_database_qaas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import qaas
import configparser
#config
config = get_config()

from model import create_all_tables

def read_qaas(file_path):
    populate_database_qaas(file_path, config)


def read_ov(folder_path):
    
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
                        print(result)
                        if "oneview_results_" in result:
                            version_prefix = f"{os.path.relpath(sub_version_path, os.path.join(folder_path, workload, program))}/"
                            process_result(os.path.join(sub_version_path, result), version_prefix)

def read_ov_french(folder_path):
    for application in os.listdir(folder_path):
        if application in ['README']:
            continue  
        application_path = os.path.join(folder_path, application)
        for tar_filename in os.listdir(application_path):
            if tar_filename.endswith('.tar.gz'):
                # extract tar files
                tar_filepath = os.path.join(application_path, tar_filename)
                print(tar_filepath)
                extracted_folder = tar_filepath.replace('.tar.gz', '')
                #  # check if the folder already exists
                if not os.path.exists(extracted_folder):
                    subprocess.run(['tar', '-xvf', tar_filepath, '-C', application_path])
                
                output_ov_dir = extracted_folder
                workload_program_name = application
                workload_program_commit_id = ""  
                qaas_timestamp = ""  
                version = tar_filename.replace('.tar.gz', '')
                # print(output_ov_dir, qaas_timestamp, version, "", version, workload_program_name, workload_program_commit_id)
                populate_database(output_ov_dir, qaas_timestamp, version, "", version, workload_program_name, workload_program_commit_id)

def main():
    # Define the argument parser
    parser = argparse.ArgumentParser(description='Run QAAS Script with Parameters')
    parser.add_argument('--data', type=str, help='Directory for the output')
    parser.add_argument('--workload', type=str, help='Workload Name')
    parser.add_argument('--version', type=str, help='Workload Version Name')
    parser.add_argument('--program', type=str,  help='Workload Program Name')
    parser.add_argument('--commit_id', type=str, help='Workload Program Commit ID')
    parser.add_argument('--ov_path', type=str, help='Read from a folder instead of arguments')
    parser.add_argument('--ov_fr_path', type=str, help='Read from a folder instead of arguments')
    parser.add_argument('--qaas_path', type=str, help='read qaas data given a file path')

    # Parse the arguments
    args = parser.parse_args()
    
 
    if args.ov_path:
        # Create all tables
        create_all_tables(config, db='oneview')
        read_ov(args.ov_path)

    elif args.ov_fr_path:
        create_all_tables(config, db='oneview')
        read_ov_french(args.ov_fr_path)

    elif args.qaas_path:
        create_all_tables(config, db='qaas')
        read_qaas(args.qaas_path)

    else:
        print("invalid flags")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        ov_web_backend_dir = os.path.join(apps_dir, 'oneview','backend')
        sys.path.append(ov_web_backend_dir)

       