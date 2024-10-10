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
# Created April 2023
# Contributors: Hafid/David

from argparse import ArgumentParser
import subprocess
import os
import sys
import json
import utils.system as system
from utils.util import split_compiler_combo
import app_builder
import shlex

script_dir=os.path.dirname(os.path.realpath(__file__))

debug_options="-g -fno-omit-frame-pointer -fcf-protection=none -no-pie -grecord-gcc-switches"

def read_compiler_flags(vendor, target):
    '''Read the list of compiler flags for a CPU vendor and a target processor.'''

    # Setup the CPU's vendor json input file.
    input_file = os.path.join(script_dir, f"compilers/{vendor}.json")
    # Read the json file
    with open(input_file, "r") as read_file:
        compiler_flags = json.load(read_file)
    #Return the list of flags for the target processor.
    return compiler_flags[target]

def filter_original_flags(orig_flags, qaas_flags):
    '''Delete all original flags that are tested/varied by QaaS logic.'''

    orig_flags_l = orig_flags.split(' ')
    qaas_flags_l = set(qaas_flags.split(' '))
    flags = ""
    for flag in orig_flags_l:
        if not flag in qaas_flags_l:
            flags += f" {flag}"
    return flags

def delete_qaas_flags_from_ninja(ninja_file, compiler, user_CC, flags):
        exclude_list = ['-x', '-march', '-mprefer-vector-width', '-qopt-zmm-usage', '-O2', '-O3', '-fno-vectorize', '-no-vec', 'fno-tree-vectorize', '-mavx', '-Ofast', '-mtune']
        # Convert QaaS flags from original to target compiler
        mapped_flags = set(flags.split(' '))
        # Read list of flags generated by Ninja
        read_ninja_flags_cmd = f"grep FLAGS {shlex.quote(ninja_file)}  | sed 's/=/:/'|cut -d':' -f2  | tr ' ' '\n' | sed '/^$/d' | sort -u"
        pipe = subprocess.Popen(read_ninja_flags_cmd, shell=True, stdout=subprocess.PIPE)
        output = pipe.communicate()[0].decode("utf-8").split('\n')
        print(output)
        # Find all the flags to exclude
        to_exclude = []
        for e in exclude_list:
            for n in output:
                index=n.find(e)
                if index != -1 and n not in mapped_flags:
                    to_exclude.append(n)
        # Build the command line to exclude all incompatible flags
        if len(to_exclude) > 0:
            cmdline = f"s:{to_exclude[0]}::g"
            for i in to_exclude[1:]:
                cmdline += f";s:{i}::g"
            cmdlines = [f"sed", "-i", f"{cmdline}", f"{ninja_file}"]
            #cmdline = f"sed -i '{cmdline}' {ninja_file}"
            cmdline = " ".join(cmdlines)
            print(cmdline)
            subprocess.run(cmdlines)
            #subprocess.run(cmdline, shell=True)

def compile_binaries(src_dir, binaries_dir, compiler_dir, orig_user_CC,
                    user_c_flags, user_cxx_flags, user_fc_flags,
                    user_link_flags, user_target, user_target_location, extra_cmake_flags, env_var_map, multi_compilers_dirs, maqao_dir):
    '''Compile the app using all available compilers.'''

    # Get the vendor name of target processor
    vendor = system.get_vendor_name()
    if vendor == 'unknown':
        printf("Unknown / unsupported vendor")
        return None
    # Get the processor architecture
    processor = system.get_intel_processor_name(maqao_dir)

    # Get the list of flags for the CPU vendor (x86, ...) and processor.
    compiler_flags = read_compiler_flags(vendor, processor)

    # Parse original user CC
    mpi_wrapper, user_CC = split_compiler_combo(orig_user_CC)

    # Save environment variables for each build per compiler and per option.
    app_envs = {}
    for compiler in compiler_flags['compilers']:
        # Nothing to do if compiler if missing environment to load
        if not compiler in multi_compilers_dirs:
            print(f"Skip {compiler}. Missing compiler environment")
            continue
        # Init array of envs
        app_envs[compiler] = []
        # Get list of QaaS target flags for 'compiler'
        options = compiler_flags['flags'][compiler]
        # Convert user provided flags from orig compiler into qaas target compiler
        filtered_c_flags = app_builder.map_compiler_flags(user_CC, compiler, user_c_flags) if user_c_flags else ""
        filtered_cxx_flags = app_builder.map_compiler_flags(user_CC, compiler, user_cxx_flags) if user_cxx_flags else ""
        filtered_fc_flags = app_builder.map_compiler_flags(user_CC, compiler, user_fc_flags) if user_fc_flags else ""

        # Itertate and build
        for option in range(len(options)):
            # Set target compiler
            target_CC = f"{mpi_wrapper}-{compiler}" if mpi_wrapper else compiler
            # Combine QaaS, debug and user provided flags in one set
            update_c_flags = f"{filtered_c_flags} {options[option]} {debug_options}"
            update_cxx_flags = f"{filtered_cxx_flags} {options[option]} {debug_options}"
            update_fc_flags = f"{filtered_fc_flags} {options[option]} {debug_options}"
            update_fc_flags = update_fc_flags.replace('-grecord-gcc-switches', '') # Unknown for FC compilers
            # Update extra CMAKE flags
            update_extra_cmake_flags = extra_cmake_flags if extra_cmake_flags else ""

            # Setup binary
            index = option + 1
            orig_binary = os.path.join(os.path.join(binaries_dir, f"{compiler}_{index}"), 'exec')

            # Add cmake's -DBUILD_SHARED_LIBS=ON if -flto is needed
            flags_set = set((update_c_flags  + " " + update_cxx_flags  + " " + update_fc_flags).split(' '))
            if '-flto' in flags_set:
                # Ignore -flto options if QaaS env var not defined
                if not "QAAS_ENABLE_LTO" in env_var_map:
                    continue
                update_extra_cmake_flags += " -DBUILD_SHARED_LIBS=ON"

            # Build originl app using user-provided compilation options
            app_builder_env = app_builder.exec(src_dir, multi_compilers_dirs[compiler], orig_binary,
                                       target_CC, target_CC, update_c_flags, update_cxx_flags, update_fc_flags,
                                       user_link_flags, user_target, user_target_location, 'prepare', update_extra_cmake_flags, f"{compiler}_{index}")
            # Add any user-provided environment variables
            app_builder_env.update(env_var_map)

            # Delete all QaaS manipulated flags frm Ninja build list
            ninja_file = os.path.join(os.path.join(src_dir, '..', f"{compiler}_{index}"), 'build.ninja')
            delete_qaas_flags_from_ninja(ninja_file, compiler, user_CC, options[option])

            # Rerun the make with updated list of flags
            app_builder.exec(src_dir, multi_compilers_dirs[compiler], orig_binary,
                                       target_CC, target_CC, update_c_flags, update_cxx_flags, update_fc_flags,
                                       user_link_flags, user_target, user_target_location, 'make', update_extra_cmake_flags, f"{compiler}_{index}", app_builder_env)
            # Add current env to list
            app_envs[compiler].append((orig_binary, app_builder_env, options[option]))

    return app_envs
