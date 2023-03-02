#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
# TO BE FIXED
# Copyright (C) 2022  Intel Corporation  All rights reserved
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

    # Specify the type of QaaS logic to run: demo (legacy) vs Stratigizer (multi-phase)
    global_parser.add_argument('--logic', help='Select the QaaS run strategy', choices=['demo', 'strategizer'], default='demo')

    # setup mutually exclusive arguments
    global_excl = global_parser.add_mutually_exclusive_group()
    add_exclusive_trace_options(global_excl)

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
