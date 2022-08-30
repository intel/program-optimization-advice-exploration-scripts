#!/usr/bin/env python3
#from argparse import ArgumentParser
import env_provisioner
import database_populator
import result_presenter
import service_submitter
import job
import os

def run(qaas_root, qaas_db_address):
  service_dir, src_url, data_url, docker_file, oneview_config, timestamp = service_submitter.get_input(qaas_root)

  src_dir, data_dir, ov_run_dir, docker_image = env_provisioner.setup_environ(service_dir, src_url, data_url, docker_file)
  # collect a list of machine to search
  machines = job.get_machines()
  # then for each machine, run experiment in container
  for machine in machines:
    mach_ov_run_dir = os.path.join(ov_run_dir, machine)
    job.launch(machine, src_dir, data_dir, oneview_config, mach_ov_run_dir, docker_image)

  # Populate results to database
  for machine in machines:
    mach_ov_run_dir = os.path.join(ov_run_dir, machine)
    database_populator.populate(mach_ov_run_dir, qaas_db_address, timestamp)

  result_presenter.show_results(qaas_db_address, timestamp)