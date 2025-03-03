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
# Contributors: David/Hafid

import os
import re
import argparse
import shutil
import subprocess
# See: https://pytrie.readthedocs.io/en/latest/ for documentation
from pytrie import StringTrie
from utils.util import load_compiler_env, split_compiler_combo
import shlex
import utils.system as system


# We use CC compiler names as compiler names and here provide lookup for different languages
compiler_map={
    "icc:CC":"icc", "icc:CXX":"icpc", "icc:FC":"ifort",
    "icx:CC":"icx", "icx:CXX":"icpx", "icx:FC":"ifx",
    "gcc:CC":"gcc", "gcc:CXX":"g++", "gcc:FC":"gfortran",
    "aocc:CC":"clang", "aocc:CXX":"clang++", "aocc:FC":"flang",
    "armclang:CC":"armclang", "armclang:CXX":"armclang++", "armclang:FC":"armflang",
    "mpiicc:CC":"mpiicc", "mpiicc:CXX":"mpiicpc", "mpiicc:FC":"mpiifort",
    "mpicc:CC":"mpicc", "mpicc:CXX":"mpic++", "mpicc:FC":"mpifort"
}

#src_dir=$(basename $(pwd))
script_dir=os.path.dirname(os.path.realpath(__file__))
src_dir=os.path.basename(script_dir)
build_dir="build"

#cd ..
#rm -rf build
# Look for flags try find grep flags
#cmake -DCMAKE_CXX_COMPILER=$user_CXX -DCMAKE_C_COMPILER=$user_CC -DCMAKE_C_FLAGS="${user_c_flags}" -DCMAKE_EXE_LINKER_FLAGS="${user_link_flags}" -S $src_dir -B $build_dir -G Ninja
#cmake -DCMAKE_CXX_COMPILER=$user_CXX -DCMAKE_C_COMPILER=$user_CC -DCMAKE_C_FLAGS="${user_c_flags}" -DCMAKE_EXE_LINKER_FLAGS="${user_link_flags}" -S $src_dir -B $build_dir
#time cmake --build $build_dir --target $user_target

# Support of compiler flag lookup
# (C1, F1, C2) ---> F2
# g(C1, F1, C2) = G(C1,F1)(C2)
# So G(C1,F1) gets a lookup function taking C2 to find the flag for C2
#  G() can be implemented by a max common prefix search with C1+F1 as string
#  G()(C2) can be implemented by replacing the leading matched prefix of C1 by the prefix of C2
def simple_replace(compiler_flag_map, compiler, flag, new_compiler):
    old_prefix=compiler_flag_map[compiler]
    new_prefix=compiler_flag_map[new_compiler]
    return re.sub(r'^'+old_prefix, new_prefix, flag)

lookup_functions = {
   "all": [
            ({'icc': 'std=gnu89', 'gcc': 'std=gnu90', 'icx': 'std=gnu90', 'aocc': 'std=gnu90', 'armclang': 'std=gnu90'}, simple_replace),
            ({'icc': 'D', 'gcc': 'D', 'icx': 'D', 'aocc': 'D', 'armclang': 'D'}, simple_replace),
            ({'icc': 'O1', 'gcc': 'O1', 'icx': 'O1', 'aocc': 'O1', 'armclang': 'O1'}, simple_replace),
            ({'icc': 'O2', 'gcc': 'O2', 'icx': 'O2', 'aocc': 'O2', 'armclang': 'O2'}, simple_replace),
            ({'icc': 'O3', 'gcc': 'O3', 'icx': 'O3', 'aocc': 'O3', 'armclang': 'O3'}, simple_replace),
            ({'icc': 'Ofast', 'gcc': 'Ofast', 'icx': 'Ofast', 'aocc': 'Ofast', 'armclang': 'Ofast'}, simple_replace),
            ({'icc': 'g', 'gcc': 'g', 'icx': 'g', 'aocc': 'g', 'armclang': 'g'}, simple_replace),
            ({'icc': 'grecord-gcc-switches', 'gcc': 'grecord-gcc-switches', 'icx': 'grecord-gcc-switches', 'aocc': 'grecord-gcc-switches', 'armclang': 'grecord-gcc-switches'}, simple_replace),
            ({'icc': 'no-pie', 'gcc': 'no-pie', 'icx': 'no-pie', 'aocc': 'no-pie', 'armclang': 'no-pie'}, simple_replace),
            ({'icc': 'fcf-protection=none', 'gcc': 'fcf-protection=none', 'icx': 'fcf-protection=none', 'aocc': 'fcf-protection=none', 'armclang': 'fcf-protection=none'}, simple_replace),
            ({'icc': 'fno-omit-frame-pointer', 'gcc': 'fno-omit-frame-pointer', 'icx': 'fno-omit-frame-pointer', 'aocc': 'fno-omit-frame-pointer', 'armclang': 'fno-omit-frame-pointer'}, simple_replace),
            ({'icc': '', 'gcc': 'Wno-implicit-function-declaration', 'icx': 'Wno-error=implicit-function-declaration', 'aocc': 'Wno-error=implicit-function-declaration', 'armclang': 'Wno-error=implicit-function-declaration'}, simple_replace),
            ({'icc': 'fpic', 'gcc': 'fpic', 'icx': 'fpic', 'aocc': 'fpic', 'armclang': 'fpic'}, simple_replace),
            ({'icc': 'qoverride-limits', 'gcc': '', 'icx': 'qoverride-limits', 'aocc': ''}, simple_replace),
            ({'icc': 'fno-alias', 'gcc': '', 'icx': 'fno-alias', 'aocc': ''}, simple_replace),
            ({'icc': 'ansi-alias', 'gcc': 'fstrict-aliasing', 'icx': 'ansi-alias', 'aocc': 'ansi-alias'}, simple_replace),
            ({'icc': 'flto', 'gcc': 'flto', 'icx': 'flto', 'aocc': 'flto', 'armclang': 'flto'}, simple_replace),
            ({'icc': 'funroll-loops', 'gcc': 'funroll-loops', 'icx': 'funroll-loops', 'aocc': 'funroll-loops', 'armclang': 'funroll-loops'}, simple_replace),
            # See http://wwwpub.zih.tu-dresden.de/~mlieber/practical_performance/05_gcc_intel_flags.pdf
            ({'icc': 'fp-model fast=2', 'gcc': 'ffast-math', 'icx': 'fp-model=fast', 'aocc': 'ffast-math', 'armclang': 'ffast-math'}, simple_replace),
            ({'icc': 'mfpmath=sse', 'gcc': 'mfpmath=sse', 'icx': 'mfpmath=sse', 'aocc': 'mfpmath=sse'}, simple_replace),
            ({'icc': 'no-vec', 'gcc': 'fno-tree-vectorize', 'icx': 'fno-vectorize', 'aocc': 'fno-vectorize', 'armclang': 'fno-vectorize'}, simple_replace),
            ({'icc': '', 'gcc': '', 'icx': 'fno-slp-vectorize', 'aocc': 'fno-slp-vectorize', 'armclang': 'fno-slp-vectorize'}, simple_replace),
            ({'icc': 'no-simd', 'gcc': '', 'icx': '', 'aocc': ''}, simple_replace),
            ({'icc': 'qno-openmp-simd', 'gcc': 'fno-openmp-simd', 'icx': 'fno-openmp-simd', 'aocc': 'fno-openmp-simd', 'armclang': 'fno-openmp-simd'}, simple_replace),
            ({'icc': 'qopt-zmm-usage=high', 'gcc': 'mprefer-vector-width=512', 'icx': 'mprefer-vector-width=512', 'aocc': 'mprefer-vector-width=512'}, simple_replace)
          ],
   "intel": [
            ({'icc': 'qopt-report=5', 'gcc': 'fsave-optimization-record', 'icx': 'qopt-report=3'}, simple_replace),
            ({'icc': 'march=native', 'gcc': 'march=native', 'icx': 'march=native'}, simple_replace),
            ({'icc': 'xSSE4.2', 'gcc': 'march=core2', 'icx': 'xSSE4.2'}, simple_replace),
            ({'icc': 'xCORE-AVX2', 'gcc': 'march=haswell', 'icx': 'xCORE-AVX2'}, simple_replace),
            ({'icc': 'xCORE-AVX512', 'gcc': 'march=skylake-avx512', 'icx': 'xCORE-AVX512'}, simple_replace),
            ({'icc': 'xSKYLAKE-AVX512', 'gcc': 'march=skylake-avx512', 'icx': 'xSKYLAKE-AVX512'}, simple_replace),
            ({'icc': 'xICELAKE-SERVER', 'gcc': 'march=icelake-server', 'icx': 'xICELAKE-SERVER'}, simple_replace),
            ({'icc': 'xSAPPHIRERAPIDS', 'gcc': 'march=sapphirerapids', 'icx': 'xSAPPHIRERAPIDS'}, simple_replace),
            ({'icc': 'qopt-mem-layout-trans=4', 'gcc': '', 'icx': 'qopt-mem-layout-trans=4'}, simple_replace)
          ],
   "amd": [
            ({'aocc': 'march=native', 'gcc': 'march=native', 'icx': 'march=native'}, simple_replace),
            ({'aocc': 'mavx2', 'gcc': 'march=haswell', 'icx': 'xCORE-AVX2'}, simple_replace),
            ({'aocc': 'march=znver3', 'gcc': 'march=znver3', 'icx': 'xCORE-AVX2'}, simple_replace),
            ({'aocc': 'march=znver4', 'gcc': 'march=znver4', 'icx': 'axCORE-AVX512'}, simple_replace),
            ({'aocc': 'march=znver5', 'gcc': 'march=znver5', 'icx': 'axCORE-AVX512'}, simple_replace)
          ],
   "arm": [
            ({'armclang': 'mcpu=native', 'gcc': 'mcpu=native'}, simple_replace),
            ({'armclang': 'mcpu=native+nosimd', 'gcc': 'mcpu=native'}, simple_replace),
            ({'armclang': 'msve-vector-bits=128', 'gcc': 'msve-vector-bits=128'}, simple_replace),
            ({'armclang': 'armpl', 'gcc': 'larmpl'}, simple_replace),
            ({'armclang': 'ffp-contract=fast', 'gcc': 'ffp-contract=fast'}, simple_replace)
          ]
   }
def encode_compiler_flag(compiler, flag):
    return compiler+':'+flag

# This trie can be used to lookup given C1 and F1
function_trie = StringTrie()
for flag_map,fn in lookup_functions["all"] + lookup_functions[system.get_vendor_name()]:
    for compiler, flag in flag_map.items():
        # Only add if the flag is not empty
        if flag:
            function_trie[encode_compiler_flag(compiler,flag)] = (flag_map, fn)

def map_compiler_flag(orig_compiler, new_compiler, orig_flag):
    try:
        flag_map,fnn = function_trie.longest_prefix_value(encode_compiler_flag(orig_compiler,orig_flag))
        return fnn(flag_map, orig_compiler, orig_flag, new_compiler)
    except:
        return None

def map_compiler_flags(orig_compiler, new_compiler, orig_flags):
    if orig_compiler == new_compiler:
        return orig_flags
    orig_flag_list = flag_str_to_list(orig_flags)
    mapped_flag_list = [map_compiler_flag(orig_compiler, new_compiler, flag) for flag in orig_flag_list]
    # remove those unmappable flags
    flags = flag_list_to_str(mapped_flag_list)
    return flags

def flag_list_to_str(mapped_flag_list):
    mapped_flag_list = ['-'+flag for flag in mapped_flag_list if flag ]
    #mapped_flag_list = orig_flag_list
    flags = " ".join(mapped_flag_list)
    return flags

def flag_str_to_list(orig_flags):
    orig_flag_list = (" "+orig_flags).split(" -")[1:]
    return orig_flag_list

def remove_underlying_flag (flags, flag):
    flag_list = flag_str_to_list(flags)
    to_remove = [item for item in flag_list if item.startswith(flag)]
    to_stay = [item for item in flag_list if item not in to_remove ]
    return flag_list_to_str(to_stay), flag_list_to_str(to_remove)

def add_underlying_flag (flags, flag, compiler):
    flag_list = flag_str_to_list(flags)
    # double check flag not in flag list
    expected_empty = [item for item in flag_list if item.startswith(flag)]
    assert len(expected_empty) == 0
    flag_list.append(f'{flag}={compiler}')
    return flag_list_to_str(flag_list)


def exec(src_dir, compiler_dir, output_binary_path, user_CC_combo, target_CC_combo,
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target, user_target_location, mode, extra_cmake_flags="", relative_build_dir="build", saved_env=None):
    # Assume we can write to parent path to source directory

    if mode == 'prepare' or mode == 'both':
        build_dir, output_dir, output_name, env = setup_build(src_dir, compiler_dir, output_binary_path, user_CC_combo, target_CC_combo, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, extra_cmake_flags, relative_build_dir)
    else:
        # For 'make' get current env for next step
        env = saved_env if saved_env != None else os.environ.copy()
        build_dir=get_build_dir(src_dir, relative_build_dir)
        output_dir=os.path.dirname(output_binary_path)
        output_name=os.path.basename(output_binary_path)

    if mode == 'make' or mode == 'both':
        build_binary(user_target, build_dir, user_target_location, env, output_dir, output_name)
    return env

def setup_build(src_dir, compiler_dir, output_binary_path, user_CC_combo, target_CC_combo, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, extra_cmake_flags="", relative_build_dir="build"):
    build_dir=get_build_dir(src_dir, relative_build_dir)
    output_dir=os.path.dirname(output_binary_path)
    output_name=os.path.basename(output_binary_path)

    cmake_c_compiler, cmake_cxx_compiler, cmake_fortran_compiler, \
        cmake_c_flags, cmake_cxx_flags, cmake_fortran_flags, cmake_linker_flags, cmake_env \
            = compute_cmake_variables(user_CC_combo, target_CC_combo, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags)

    shutil.rmtree(build_dir, ignore_errors=True)
    my_env = os.environ.copy()
    # setup env
    print(f"compiler_dir={compiler_dir}")
    env = load_compiler_env(compiler_dir)

    #subprocess.run('icc --version', shell=True, env=env)
    if cmake_env: env.update(cmake_env)

    cmake_config_cmds=[f'cmake',
        f'-DCMAKE_CXX_COMPILER={cmake_cxx_compiler}',
        f'-DCMAKE_C_COMPILER={cmake_c_compiler}',
        f'-DCMAKE_Fortran_COMPILER={cmake_fortran_compiler}',
        '-DCMAKE_EXPORT_COMPILE_COMMANDS=1',
        f'-DCMAKE_C_FLAGS={shlex.quote(cmake_c_flags)}',
        f'-DCMAKE_CXX_FLAGS={shlex.quote(cmake_cxx_flags)}',
        f'-DCMAKE_Fortran_FLAGS={shlex.quote(cmake_fortran_flags)}',
        f'-DCMAKE_EXE_LINKER_FLAGS={shlex.quote(cmake_linker_flags)}']
    cmake_config_cmds.extend(shlex.split(extra_cmake_flags))
    cmake_config_cmds.extend([f'-S', f'{src_dir}', '-B', f'{build_dir}', '-G', 'Ninja'])
    #cmake_config_cmd=f'cmake -DCMAKE_CXX_COMPILER={cmake_cxx_compiler} -DCMAKE_C_COMPILER={cmake_c_compiler} '\
    #    f'-DCMAKE_Fortran_COMPILER={cmake_fortran_compiler} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 '\
    #    f'-DCMAKE_C_FLAGS="{cmake_c_flags}" '\
    #    f'-DCMAKE_CXX_FLAGS="{cmake_cxx_flags}" '\
    #    f'-DCMAKE_Fortran_FLAGS="{cmake_fortran_flags}" '\
    #    f'-DCMAKE_EXE_LINKER_FLAGS="{cmake_linker_flags}" '\
    #    f'{extra_cmake_flags} '\
    #    f'-S {src_dir} -B {build_dir} -G Ninja > {os.path.dirname(src_dir)}/qaas_build.log 2>&1'
    cmake_config_cmd = " ".join(cmake_config_cmds)
    print(cmake_config_cmd)
    env['VERBOSE']='1'
    log_file_name = os.path.join(os.path.dirname(src_dir), "qaas_build.log")
    with open(log_file_name, 'w') as log_file:
        subprocess.run(cmake_config_cmds, stdout=log_file, stderr=subprocess.STDOUT, env=env, text=True)
    shutil.move(log_file_name, build_dir)
    # Allow search any compiler generated files
    env['QAAS_BUILD_DIR']=build_dir
    return build_dir, output_dir, output_name, env

def compute_cmake_variables(user_CC_combo, target_CC_combo, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags):
    user_mpi_compiler, user_suite, user_CC, user_CXX, user_FC = parse_compiler_combo(user_CC_combo)
    target_mpi_compiler, target_suite, target_CC, target_CXX, target_FC = parse_compiler_combo(target_CC_combo)
    # TODO: some checks can be done about mpi compiler choices (e.g. if we want to ensure both are the same)
    # Right now just use the target_mpi_compiler choice
    if user_mpi_compiler:
        pass
    else:
        pass

    cmake_env = None
    if target_mpi_compiler:
        # MPI build, ensure MPI wrappers are specified in cmake_*_compilers and provide flags like -cxx to point to target compilers
        if target_mpi_compiler == 'mpiicc':
            # Intel wrapper
            cmake_c_compiler = 'mpiicc'
            cmake_cxx_compiler = 'mpiicpc'
            cmake_fortran_compiler = 'mpif90' if target_FC == 'gfortran' else 'mpiifort'
            user_c_flags, removed_c_flags = remove_underlying_flag (user_c_flags, "cc")
            user_cxx_flags, removed_cxx_flags = remove_underlying_flag (user_cxx_flags, "cxx")
            user_fc_flags, removed_fc_flags = remove_underlying_flag (user_fc_flags, "fc")
        elif target_mpi_compiler == 'mpicc':
            # Open MPI wrapper
            cmake_c_compiler = 'mpicc'
            cmake_cxx_compiler = 'mpic++'
            cmake_fortran_compiler = 'mpifort'
            cmake_env = { "OMPI_CC": target_CC, "OMPI_CXX": target_CXX, "OMPI_FC": target_FC }
        elif target_mpi_compiler == 'opalcc':
            # OPAL wrapper
            cmake_c_compiler = 'opalcc'
            cmake_cxx_compiler = 'opalc++'
            cmake_fortran_compiler = ''
            cmake_env = { "OPAL_CC": target_CC, "OPAL_CXX": target_CXX }
        pass
    else:
        # Not MPI build
        cmake_c_compiler = target_CC
        cmake_cxx_compiler = target_CXX
        cmake_fortran_compiler = target_FC

    cmake_c_flags = map_compiler_flags(user_suite, target_suite, user_c_flags)
    cmake_cxx_flags = map_compiler_flags(user_suite, target_suite, user_cxx_flags)
    cmake_fortran_flags = map_compiler_flags(user_suite, target_suite, user_fc_flags)
    cmake_linker_flags = map_compiler_flags(user_suite, target_suite, user_link_flags)

    if target_mpi_compiler == 'mpiicc':
        cmake_c_flags = add_underlying_flag (cmake_c_flags, "cc", target_CC)
        cmake_cxx_flags = add_underlying_flag (cmake_cxx_flags, "cxx", target_CXX)
        if cmake_fortran_compiler == 'mpiifort':
            cmake_fortran_flags = add_underlying_flag (cmake_fortran_flags, "fc", target_FC)


    return cmake_c_compiler, cmake_cxx_compiler, cmake_fortran_compiler, \
        cmake_c_flags, cmake_cxx_flags, cmake_fortran_flags, cmake_linker_flags, \
            cmake_env

def parse_compiler_combo(CC_combo):
    mpi_wrapper, compiler_suite = split_compiler_combo(CC_combo)

    CC = compiler_map[compiler_suite+":CC"]
    CXX = compiler_map[compiler_suite+":CXX"]
    FC = compiler_map[compiler_suite+":FC"]
    return mpi_wrapper, compiler_suite, CC,CXX,FC


def get_build_dir(src_dir, relative_build_dir):
    return os.path.join(src_dir, '..', relative_build_dir)

def build_binary(user_target, build_dir, target_location, env, output_dir, output_name):
    cmake_target = user_target if user_target else 'all'
    cmake_build_cmds=[f'/usr/bin/time', '-p', 'cmake', '--build', f'{build_dir}', '--target', f'{cmake_target}']
    #cmake_build_cmd=f'/usr/bin/time -p cmake --build {build_dir} --target {cmake_target} >> {build_dir}/qaas_build.log 2>&1'
    cmake_build_cmd = " ".join(cmake_build_cmds)
    print(cmake_build_cmd)
    log_file_name = os.path.join(build_dir, "qaas_build.log")
    with open(log_file_name, "a") as log_file:
        subprocess.run(cmake_build_cmds, stdout=log_file, stderr=subprocess.STDOUT, text=True, env=env)
    built_bin = os.path.join(build_dir, target_location)
    out_bin = os.path.join(output_dir, output_name)
    print(f"Copying executable: {built_bin} -> {out_bin}")
    os.makedirs(output_dir, exist_ok=True)
    if os.path.islink(out_bin):
        os.remove(out_bin)
    os.symlink(built_bin, out_bin)
    print(f"Binary executable saved to: {out_bin}")

def get_languages_in_project(build_dir):
   '''Search for enabled programming languages in project.'''

   # Define QaaS-supported languages
   supported_languages = ['C', 'CXX', 'Fortran']
   # Open build log file (ninja)
   with open(os.path.join(build_dir, "build.ninja")) as f:
        build_log = f.read()
   # Detect programming languages
   languages = []
   for lang in supported_languages:
        matched = re.search(f"{lang}_COMPILER", build_log, re.MULTILINE)
        if matched:
            languages.append(lang)
   return '/'.join([str(lang) for lang in languages])

def build_argparser(parser, include_binary_path=True, include_mode=True):
    parser.add_argument('--src-dir', help='Source tree path', required=True)
    parser.add_argument('--compiler-dir', help='Path to compiler', required=True)
    if include_binary_path:
        parser.add_argument('--output-binary-path', help='Path to place the binary executable', required=True)
    parser.add_argument('--orig-user-CC', help='Original assumed compiler', required=True)
    parser.add_argument('--target-CC', help='Target compiler for this build', required=True)
    parser.add_argument('--user-c-flags', help='C flags provided by user', required=True)
    parser.add_argument('--user-cxx-flags', help='CXX flags provided by user', required=True)
    parser.add_argument('--user-fc-flags', help='Fortran flags provided by user', required=True)
    parser.add_argument('--user-link-flags', help='Link flags provided by user', required=True)
    parser.add_argument('--user-target', help='Target for this build', required=True)
    parser.add_argument('--user-target-location', help='Target location for this build (executable in build directory)', required=True)
    if include_mode:
        parser.add_argument('--mode', help='Mode of build', choices=['prepare', 'make', 'both'], required=True)
    parser.add_argument('--extra-cmake-flags', type=str, help='Extra CMAKE Flags for this build', default="\"\"")
    parser.add_argument('--build-dir', type=str, help='Build directort', default="build")

# For sample inputs: see VSCode launch.json file

def main():
    parser = argparse.ArgumentParser(description="Build application")
    build_argparser(parser)
    args = parser.parse_args()

    exec(args.src_dir, args.compiler_dir, args.output_binary_path, args.orig_user_CC, args.target_CC,
         args.user_c_flags, args.user_cxx_flags, args.user_fc_flags, args.user_link_flags, args.user_target, args.user_target_location, args.mode, args.extra_cmake_flags, args.build_dir)


if __name__ == "__main__":
    main()


