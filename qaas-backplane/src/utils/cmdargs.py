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
# Created October 2022
# Contributors: Hafid/David

import os
import sys
import logging
import argparse

def add_exclusive_trace_options(excl_parser):
    """Populate a parser with exclusive general trace options."""
    excl_parser.add_argument("-D", "--debug", action="store_true", help="debug mode")
    excl_parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode")

def add_exclusive_container_options(excl_parser):
    """Populate a parser with exclusive container options."""
    # Specify whether to disable container mode
    excl_parser.add_argument('-nc', "--no-container", action="store_true", help="Disable container mode")
    # Specify whether to run root in container (permissive rootless mode)
    excl_parser.add_argument('-r', "--as-root-in-container", action="store_true", help="Run host users as root in container [permissive rootless mode in podman]. Not allowed for true root users.")

def parse_cli_args(argv):
    """Process the command line arguments."""
    if len(argv) == 1:
        argv.append('-h')

    # create the top-level parser
    global_parser = argparse.ArgumentParser(prog=os.path.basename(argv[0]),
                                            description="This is QaaS backend service.",
                                            epilog="")

    # add the application parameerts JSON input file option
    global_parser.add_argument('-ap', '--app-params', type=str, dest='app_params', metavar='<input-file>',
                            help='name the input file (including suffix)', required=True)

    # setup mutually exclusive arguments
    global_excl = global_parser.add_mutually_exclusive_group()
    add_exclusive_trace_options(global_excl)

    # setup mutually exclusive container arguments
    container_excl = global_parser.add_mutually_exclusive_group()
    add_exclusive_container_options(container_excl)

    # Specify whether to disable QaaS search for best default compiler
    global_parser.add_argument('-ncd', "--no-compiler-default", action="store_true", help="Disable search for best default compiler")
    # Specify whether to disable QaaS search for best compiler flags
    global_parser.add_argument('-ncf', "--no-compiler-flags", action="store_true", help="Disable search for best compiler flags")

    # Force usage of parallel run for compiler search
    global_parser.add_argument('-p', '--parallel-compiler-runs', choices=['auto', 'off', 'mpi', 'openmp', 'hybrid'], default='auto',
                               help="Force multiprocessing [auto, MPI, OpenMP or hybrid] for compiler search runs")

    # Turn ON multicore/parallel scalability runs
    global_parser.add_argument('-s', '--enable-parallel-scale', nargs='?', default=0, const='full', choices=['best-compiler','full'], help="Turn on multicore scalability runs (optional). If not set, default is no scalability runs. If set, option is 'full' by default to runs scalability runs for each compiler. If set with 'best-compiler', scalability runs only using best compiler/options ", required=False)

    # Specify whether QaaS runs are to be perfomed on the local system (avoid ssh)
    global_parser.add_argument('-l', '--local-job', action="store_true", help="Enable ssh-less job runs on the local machine", required=False)

    # Specify location where to put QaaS reports after run termination
    global_parser.add_argument('-o', '--output-dir', type=str, dest='output_dir', metavar='<reports-dir>', default='./qaas_out', help='base directory where to put generated QaaS reports. Default is $PWD/qaas_out/')

    # parse arguments
    args = global_parser.parse_args()

    # configure logging
    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    return args
