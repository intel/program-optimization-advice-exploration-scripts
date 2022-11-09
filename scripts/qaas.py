#!/usr/bin/env python3
# Contributors: Hafid/David
#from argparse import ArgumentParser
import env_provisioner
import database_populator
import result_presenter
import service_submitter
import job
import os
import util

compiler_subdir_map = { 'icc:2022': 'intel/2022', 'icc:19.1': 'intel/19.1',
                       'icx:2022': 'intel/2022', 'icx:19.1': 'intel/19.1',
                       'gcc:11.1': 'gcc/gcc-11.1', 'gcc:11.1': 'gcc/gcc-11.1' }

def run(qaas_root, qaas_db_address, qaas_compiler_dir, qaas_ov_dir):
  service_dir, src_url, data_url, docker_file, oneview_config, timestamp, \
    orig_user_CC, user_c_flags, user_cxx_flags, user_fc_flags, \
      user_link_flags, user_target, user_target_location, env_var_map, run_cmd = service_submitter.get_input(qaas_root)

  src_dir, data_dir, ov_run_dir, locus_run_dir, docker_image = env_provisioner.setup_environ(service_dir, src_url, data_url, docker_file)
  # collect a list of machine to search
  machines = job.get_machines()
  # then for each machine, run experiment in container
  for machine in machines:
    mach_ov_run_dir = util.make_dir(os.path.join(ov_run_dir, machine))
    for target_CC, target_CC_VERSION in [('icc', '2022')]:
      # Details TBD about compiler path map
      compiler_subdir = compiler_subdir_map[target_CC+":"+target_CC_VERSION]
      mach_locus_run_dir = util.make_dir(os.path.join(locus_run_dir, machine, target_CC))
      job.launch(machine, src_dir, data_dir, oneview_config, mach_ov_run_dir, mach_locus_run_dir, docker_image, \
        os.path.join(qaas_compiler_dir, compiler_subdir), qaas_ov_dir,
        orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
        user_link_flags, user_target, user_target_location, env_var_map, run_cmd)

  # Populate results to database
  for machine in machines:
    mach_ov_run_dir = os.path.join(ov_run_dir, machine)
    database_populator.populate(mach_ov_run_dir, qaas_db_address, timestamp)

  result_presenter.show_results(qaas_db_address, timestamp)