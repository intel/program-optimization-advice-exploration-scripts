# Contributors: Hafid/David
from argparse import ArgumentParser
import subprocess
import os
import sys
import app_builder

script_dir=os.path.dirname(os.path.realpath(__file__))

options=["-O3 -march=native", "-O3 -march=native -mprefer-vector-width=256"]

debug_options="-g -grecord-command-line -fno-omit-frame-pointer"

def compile_binaries(src_dir, base_run_dir, compiler_dir, orig_user_CC, 
                    target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                    user_link_flags, user_target, user_target_location, extra_cmake_flags):

    '''Compile the app using all available compilers.'''
    app_envs = []
    for option in range(2):
        print(f"Buid with: {options[option]}")
        # Update flags
        update_c_flags = f"{user_c_flags} {options[option]} {debug_options}" if user_c_flags else "" 
        update_cxx_flags = f"{user_cxx_flags} {options[option]} {debug_options}" if user_cxx_flags else "" 
        update_fc_flags = f"{user_fc_flags} {options[option]} {debug_options}" if user_fc_flags else "" 

        # Setup binary
        base_run_dir_orig = os.path.join(base_run_dir, f"UP/{target_CC}_{option}")
        orig_binary = os.path.join(base_run_dir_orig, 'exec')

        # Build originl app using user-provided compilation options
        app_builder_env = app_builder.exec(src_dir, compiler_dir, orig_binary, 
                                   orig_user_CC, target_CC, user_c_flags, user_cxx_flags, user_fc_flags,
                                   user_link_flags, user_target, user_target_location, 'both', extra_cmake_flags, f"{target_CC}_{option}")
        # Add current env to list 
        app_envs.append((orig_binary, app_builder_env))

    return app_envs
