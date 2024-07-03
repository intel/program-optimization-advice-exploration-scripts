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
# Created Feburary 2024
# Contributors: Hafid/David

import os
import sys
import subprocess
import configparser
import utils.system as system
from app_builder import get_languages_in_project

# constants
QAAS_SECTION_NAME = "QAAS"
SYSTEM_SECTION_NAME = "SYSTEM"
REPORTS_SECTION_NAME = "REPORTS"

class QAASMetaDATA:
    def __init__(self, qaas_reports_dir, file_name="input.txt"):
        self.qaas_reports_dir = qaas_reports_dir
        self.metadata_pathname = os.path.join(self.qaas_reports_dir, file_name)
        self.config = configparser.ConfigParser()
        self.config.optionxform=str
        if not os.path.isfile(self.metadata_pathname):
            self.config[QAAS_SECTION_NAME] = {}
            self.config[REPORTS_SECTION_NAME] = {}
            self.config[SYSTEM_SECTION_NAME] = {}
            self.write_data(self.config)
        self.config.read(self.metadata_pathname)

    def write_data(self, meta_config_parser):
        with open(self.metadata_pathname, 'w') as meta_config_file:
            meta_config_parser.write(meta_config_file)

    @property
    def qaas_rundir(self):
        return os.path.dirname(self.qaas_reports_dir)

    @property
    def qaas_appname(self):
        return os.path.basename(os.path.dirname(self.qaas_rundir))

    @property
    def qaas_timestamp(self):
        return os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(self.qaas_rundir))))

    @property
    def qaas_dataset_label(self):
        dataset_file_path = os.path.join(os.path.dirname(self.qaas_rundir), "dataset", "dataset_label.txt")
        return subprocess.check_output([f"cat", f"{dataset_file_path}"]).decode("utf-8")
        #return subprocess.check_output(f"cat {dataset_file_path}", shell=True).decode("utf-8")

    @property
    def qaas_lang_in_project(self):
        return get_languages_in_project(os.path.join(os.path.dirname(self.qaas_rundir), "build", "build"))

    def add_qaas_metadata(self, run_cmd, dataset_name=""):
        self.config[QAAS_SECTION_NAME]["timestamp"] = self.qaas_timestamp
        self.config[QAAS_SECTION_NAME]["app_name"] = self.qaas_appname
        self.config[QAAS_SECTION_NAME]["git_commit"] = ''
        self.config[QAAS_SECTION_NAME]["dataset_name"] = self.qaas_dataset_label
        self.config[QAAS_SECTION_NAME]["run_cmd"] = run_cmd
        self.write_data(self.config)

    def add_prog_lang_metadata(self):
        self.config[QAAS_SECTION_NAME]["LANG"] = self.qaas_lang_in_project
        self.write_data(self.config)

    def add_multicompiler_metadata(self, default_compiler, report_name):
        self.config.optionxform=str
        self.config[REPORTS_SECTION_NAME]["compiler_default"] = default_compiler
        self.config[REPORTS_SECTION_NAME]["multicompiler_report"] = report_name
        self.write_data(self.config)

    def add_scalability_metadata(self, mpi_scaling, omp_scaling, report_name="", scalability_reference_line=""):
        if mpi_scaling != "":
            self.config[REPORTS_SECTION_NAME]["mpi_scaling"] = mpi_scaling
        if omp_scaling != "":
            self.config[REPORTS_SECTION_NAME]["openmp_scaling"] = omp_scaling
        self.config[REPORTS_SECTION_NAME]["scalability_report"] = report_name
        self.config[REPORTS_SECTION_NAME]["scalability_reference_line"] = f'{scalability_reference_line}'
        self.write_data(self.config)

    def add_figure_of_merit_metadata(self, metric_type="NA"):
        self.config[REPORTS_SECTION_NAME]["figure_of_merit_type"] = metric_type
        self.write_data(self.config)

    def add_system_metadata(self, maqao_dir):
        # System info
        self.config[SYSTEM_SECTION_NAME]["machine"] = system.get_hostname()
        self.config[SYSTEM_SECTION_NAME]["model_name"] = system.get_model_name()
        self.config[SYSTEM_SECTION_NAME]["ISA"] = system.get_ISA()
        self.config[SYSTEM_SECTION_NAME]["architecture"] = system.get_processor_architecture(maqao_dir)
        # CPU info
        self.config[SYSTEM_SECTION_NAME]["number_of_cpus"] = str(system.get_number_of_cpus())
        self.config[SYSTEM_SECTION_NAME]["number_of_cores"] = str(system.get_number_of_cores())
        self.config[SYSTEM_SECTION_NAME]["number_of_sockets"] = str(system.get_number_of_sockets())
        self.config[SYSTEM_SECTION_NAME]["number_of_cores_per_socket"] = str(int(system.get_number_of_cores()/system.get_number_of_sockets()) )
        self.config[SYSTEM_SECTION_NAME]["number_of_numa_domains"] = str(system.get_number_of_nodes())
        # CPUFreq settings
        self.config[SYSTEM_SECTION_NAME]["frequency_driver"] = system.get_frequency_driver()
        self.config[SYSTEM_SECTION_NAME]["frequency_governor"] = system.get_frequency_governor()
        self.config[SYSTEM_SECTION_NAME]["scaling_max_frequency"] = system.get_scaling_max_frequency()
        self.config[SYSTEM_SECTION_NAME]["scaling_min_frequency"] = system.get_scaling_min_frequency()
        self.config[SYSTEM_SECTION_NAME]["advertized_frequency"] = system.get_advertized_frequency()
        self.config[SYSTEM_SECTION_NAME]["maximal_frequency"] = system.get_maximal_frequency()
        # MEM settings
        self.config[SYSTEM_SECTION_NAME]["huge_pages"] = system.get_THP_policy()
        self.write_data(self.config)

    def add_compiler_version(self, compiler, compiler_dir):
        self.config[SYSTEM_SECTION_NAME][f"{compiler}_version"] = system.get_compiler_version(compiler, compiler_dir)
        self.write_data(self.config)
