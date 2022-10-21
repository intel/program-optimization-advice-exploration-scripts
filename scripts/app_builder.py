import os
import re
import argparse
import shutil
import subprocess
# See: https://pytrie.readthedocs.io/en/latest/ for documentation
from pytrie import StringTrie
from util import load_compiler_env


# We use CC compiler names as compiler names and here provide lookup for different languages
compiler_map={
    "icc:CC":"icc", "icc:CXX":"icpc", "icc:FC":"ifort",
    "icx:CC":"icx", "icx:CXX":"icpx", "icx:FC":"ifx",
    "gcc:CC":"gcc", "gcc:CXX":"g++", "gcc:FC":"gfortran",
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

lookup_functions = [ 
            ({'icc': 'D', 'gcc': 'D', 'icx': 'D'}, simple_replace),
            ({'icc': 'O1', 'gcc': 'O1', 'icx': 'O1'}, simple_replace),
            ({'icc': 'O2', 'gcc': 'O2', 'icx': 'O2'}, simple_replace),
            ({'icc': 'g', 'gcc': 'g', 'icx': 'g'}, simple_replace),
            ({'icc': 'fpic', 'gcc': 'fpic', 'icx': 'fpic'}, simple_replace),
            ({'icc': 'qno-offload', 'gcc': 'foffload=disable', 'icx': '-offload=-'}, simple_replace),
            ({'icc': 'fno-alias', 'gcc': '', 'icx': 'fno-alias'}, simple_replace),
            # See http://wwwpub.zih.tu-dresden.de/~mlieber/practical_performance/05_gcc_intel_flags.pdf
            ({'icc': 'ansi-alias', 'gcc': 'fstrict-aliasing', 'icx': 'ansi-alias'}, simple_replace),
            ({'icc': 'fp-model fast=2', 'gcc': 'ffast-math', 'icx': 'fp-model fast'}, simple_replace),
            ({'icc': 'qoverride-limits', 'gcc': '', 'icx': 'qoverride-limits'}, simple_replace),
            ({'icc': 'xCore-AVX512', 'gcc': 'mavx512f', 'icx': 'xCore-AVX512'}, simple_replace),
            ({'icc': 'qopt-zmm-usage=high', 'gcc': '', 'icx': 'mprefer-vector-width=512'}, simple_replace),
            ({'icc': 'O3', 'gcc': 'O3', 'icx': 'O3'}, simple_replace)
            ]
def encode_compiler_flag(compiler, flag):
    return compiler+':'+flag

# This trie can be used to lookup given C1 and F1
function_trie = StringTrie()
for flag_map,fn in lookup_functions:
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
    orig_flag_list = (" "+orig_flags).split(" -")[1:]
    mapped_flag_list = [map_compiler_flag(orig_compiler, new_compiler, flag) for flag in orig_flag_list]
    # remove those unmappable flags
    mapped_flag_list = ['-'+flag for flag in mapped_flag_list if flag ]
    #mapped_flag_list = orig_flag_list
    flags = " ".join(mapped_flag_list)
    return flags

def exec(src_dir, compiler_dir, relative_binary_path, orig_user_CC, user_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target, mode):
    # Assume we can write to parent path to source directory

    if mode == 'prepare' or mode == 'both': 
        build_dir, output_dir, output_name, env = setup_build(src_dir, compiler_dir, relative_binary_path, orig_user_CC, user_CC, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags)
    else:
        # For 'make' get current env for next step
        env = os.environ.copy()
        build_dir=get_build_dir(src_dir)
        output_dir=os.path.dirname(relative_binary_path)
        output_name=os.path.basename(relative_binary_path)
        
    if mode == 'make' or mode == 'both': 
        build_binary(user_target, build_dir, env, output_dir, output_name)

def setup_build(src_dir, compiler_dir, relative_binary_path, orig_user_CC, user_CC, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags):
    build_dir=get_build_dir(src_dir)
    output_dir=os.path.dirname(relative_binary_path)
    output_name=os.path.basename(relative_binary_path)
    user_CXX=compiler_map[user_CC+":CXX"]
    user_FC=compiler_map[user_CC+":FC"]

    shutil.rmtree(build_dir, ignore_errors=True)
    my_env = os.environ.copy()
    # setup env
    #subprocess.run("/bin/bash -c 'source /nfs/site/proj/openmp/compilers/intel/2022/Linux/intel64/load.sh --force && env > /tmp/env.txt'", shell=True, env=my_env)
    env = load_compiler_env(compiler_dir)

    #print(env)
    #read(x)
    subprocess.run('icc --version', shell=True, env=env)
    #my_env=env
    
    cmake_config_cmd=f'cmake -DCMAKE_CXX_COMPILER={user_CXX} -DCMAKE_C_COMPILER={user_CC} '\
        f'-DCMAKE_Fortran_COMPILER={user_FC} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 '\
        f'-DCMAKE_C_FLAGS="{map_compiler_flags(orig_user_CC, user_CC, user_c_flags)}" '\
        f'-DCMAKE_CXX_FLAGS="{map_compiler_flags(orig_user_CC, user_CC, user_cxx_flags)}" '\
        f'-DCMAKE_Fortran_FLAGS="{map_compiler_flags(orig_user_CC, user_CC, user_fc_flags)}" '\
        f'-DCMAKE_EXE_LINKER_FLAGS="{map_compiler_flags(orig_user_CC, user_CC, user_link_flags)}" '\
        f'-S {src_dir} -B {build_dir} -G Ninja -DCMAKE_RUNTIME_OUTPUT_DIRECTORY={output_dir}'
    print(cmake_config_cmd)
    env['VERBOSE']='1'
    subprocess.run(cmake_config_cmd, shell=True, env=env)
    return build_dir, output_dir, output_name, env

def get_build_dir(src_dir):
    return os.path.join(src_dir, '..', 'build')

def build_binary(user_target, build_dir, env, output_dir, output_name):
    cmake_build_cmd=f'time cmake --build {build_dir} --target {user_target}'
    subprocess.run(cmake_build_cmd, shell=True, env=env)
    os.rename(os.path.join(output_dir, user_target), os.path.join(output_dir, output_name))



def build_argparser(parser, include_binary_path=True, include_mode=True):
    parser.add_argument('--src-dir', help='Source tree path', required=True)
    parser.add_argument('--compiler-dir', help='Path to compiler', required=True)
    if include_binary_path:
        parser.add_argument('--relative-binary-path', help='Path to binary executable', required=True)
    parser.add_argument('--orig-user-CC', help='Original assumed compiler', required=True)
    parser.add_argument('--target-CC', help='Target compiler for this build', required=True)
    parser.add_argument('--user-c-flags', help='C flags provided by user', required=True)
    parser.add_argument('--user-cxx-flags', help='CXX flags provided by user', required=True)
    parser.add_argument('--user-fc-flags', help='Fortran flags provided by user', required=True)
    parser.add_argument('--user-link-flags', help='Link flags provided by user', required=True)
    parser.add_argument('--user-target', help='Target for this build', required=True)
    if include_mode:
        parser.add_argument('--mode', help='Mode of build', choices=['prepare', 'make', 'both'], required=True)

# For sample inputs: see VSCode launch.json file

def main():
    parser = argparse.ArgumentParser(description="Build application")
    build_argparser(parser)
    args = parser.parse_args()

    exec(args.src_dir, args.compiler_dir, args.relative_binary_path, args.orig_user_CC, args.target_CC,
         args.user_c_flags, args.user_cxx_flags, args.user_fc_flags, args.user_link_flags, args.user_target, args.mode)


if __name__ == "__main__": 
    main()


