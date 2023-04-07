import os
import re
import argparse
import shutil
import subprocess
# See: https://pytrie.readthedocs.io/en/latest/ for documentation
from pytrie import StringTrie
from utils.util import load_compiler_env, split_compiler_combo


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
            ({'icc': 'O3', 'gcc': 'O3', 'icx': 'O3'}, simple_replace),
            ({'icc': 'fpic', 'gcc': 'fpic', 'icx': 'fpic'}, simple_replace),
            ({'icc': 'qno-offload', 'gcc': 'foffload=disable', 'icx': '-offload=-'}, simple_replace),
            ({'icc': 'fno-alias', 'gcc': '', 'icx': 'fno-alias'}, simple_replace),
            # See http://wwwpub.zih.tu-dresden.de/~mlieber/practical_performance/05_gcc_intel_flags.pdf
            ({'icc': 'ansi-alias', 'gcc': 'fstrict-aliasing', 'icx': 'ansi-alias'}, simple_replace),
            ({'icc': 'fp-model fast=2', 'gcc': 'ffast-math', 'icx': 'fp-model fast'}, simple_replace),
            ({'icc': 'qoverride-limits', 'gcc': '', 'icx': 'qoverride-limits'}, simple_replace),
            ({'icc': 'no-vec', 'gcc': 'fno-tree-vectorize', 'icx': 'no-vec'}, simple_replace),
            ({'icc': 'no-simd', 'gcc': '', 'icx': 'no-simd'}, simple_replace),
            ({'icc': 'xCore-AVX2', 'gcc': 'march=haswell', 'icx': 'xCore-AVX2'}, simple_replace),
            ({'icc': 'xCore-AVX512', 'gcc': 'march=skylake-avx512', 'icx': 'xCore-AVX512'}, simple_replace),
            ({'icc': 'qopt-zmm-usage=high', 'gcc': 'mprefer-vector-width=512', 'icx': 'mprefer-vector-width=512'}, simple_replace),
            ({'icc': 'g', 'gcc': 'g', 'icx': 'g'}, simple_replace),
            ({'icc': 'no-pie', 'gcc': '', 'icx': 'no-pie'}, simple_replace),
            ({'icc': 'fce-protection=none', 'gcc': '', 'icx': 'fce-protection=none'}, simple_replace),
            ({'icc': 'grecord-gcc-switches', 'gcc': '', 'icx': 'grecord-gcc-switches'}, simple_replace),
            ({'icc': 'fno-omit-frame-pointer', 'gcc': 'fno-omit-frame-pointer', 'icx': 'fno-omit-frame-pointer'}, simple_replace)
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
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target, user_target_location, mode, extra_cmake_flags="", relative_build_dir="build"):
    # Assume we can write to parent path to source directory

    if mode == 'prepare' or mode == 'both': 
        build_dir, output_dir, output_name, env = setup_build(src_dir, compiler_dir, output_binary_path, user_CC_combo, target_CC_combo, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, extra_cmake_flags, relative_build_dir)
    else:
        # For 'make' get current env for next step
        env = os.environ.copy()
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
    user_mpi_compiler, user_CC, user_CXX, user_FC = parse_compiler_combo(user_CC_combo)
    target_mpi_compiler, target_CC, target_CXX, target_FC = parse_compiler_combo(target_CC_combo)

    cmake_c_compiler, cmake_cxx_compiler, cmake_fortran_compiler, \
        cmake_c_flags, cmake_cxx_flags, cmake_fortran_flags, cmake_linker_flags, cmake_env \
            = compute_cmake_variables(user_mpi_compiler, target_mpi_compiler, user_CC, target_CC, target_CXX, target_FC, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags)


    shutil.rmtree(build_dir, ignore_errors=True)
    my_env = os.environ.copy()
    # setup env
    #subprocess.run("/bin/bash -c 'source /nfs/site/proj/openmp/compilers/intel/2022/Linux/intel64/load.sh --force && env > /tmp/env.txt'", shell=True, env=my_env)
    env = load_compiler_env(compiler_dir)

    #print(env)
    #read(x)
    subprocess.run('icc --version', shell=True, env=env)
    #my_env=env
    if cmake_env: env.update(cmake_env)
    
    cmake_config_cmd=f'cmake -DCMAKE_CXX_COMPILER={cmake_cxx_compiler} -DCMAKE_C_COMPILER={cmake_c_compiler} '\
        f'-DCMAKE_Fortran_COMPILER={cmake_fortran_compiler} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 '\
        f'-DCMAKE_C_FLAGS="{cmake_c_flags}" '\
        f'-DCMAKE_CXX_FLAGS="{cmake_cxx_flags}" '\
        f'-DCMAKE_Fortran_FLAGS="{cmake_fortran_flags}" '\
        f'-DCMAKE_EXE_LINKER_FLAGS="{cmake_linker_flags}" '\
        f'{extra_cmake_flags} '\
        f'-S {src_dir} -B {build_dir} -G Ninja '
    #    f'-DCMAKE_RUNTIME_OUTPUT_DIRECTORY={output_dir}'
    print(cmake_config_cmd)
    env['VERBOSE']='1'
    subprocess.run(cmake_config_cmd, shell=True, env=env)
    return build_dir, output_dir, output_name, env

def compute_cmake_variables(user_mpi_compiler, target_mpi_compiler, user_CC, target_CC, target_CXX, target_FC, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags):
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
            cmake_fortran_compiler = 'mpiifort'
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

    cmake_c_flags = map_compiler_flags(user_CC, target_CC, user_c_flags)
    cmake_cxx_flags = map_compiler_flags(user_CC, target_CC, user_cxx_flags)
    cmake_fortran_flags = map_compiler_flags(user_CC, target_CC, user_fc_flags)
    cmake_linker_flags = map_compiler_flags(user_CC, target_CC, user_link_flags)

    if target_mpi_compiler == 'mpiicc':
        cmake_c_flags = add_underlying_flag (cmake_c_flags, "cc", target_CC)
        cmake_cxx_flags = add_underlying_flag (cmake_cxx_flags, "cxx", target_CXX)
        cmake_fortran_flags = add_underlying_flag (cmake_fortran_flags, "fc", target_FC)


    return cmake_c_compiler, cmake_cxx_compiler, cmake_fortran_compiler, \
        cmake_c_flags, cmake_cxx_flags, cmake_fortran_flags, cmake_linker_flags, \
            cmake_env

def parse_compiler_combo(CC_combo):
    mpi_wrapper, CC = split_compiler_combo(CC_combo)
        
    CXX = compiler_map[CC+":CXX"]
    FC = compiler_map[CC+":FC"]
    return mpi_wrapper, CC,CXX,FC


def get_build_dir(src_dir, relative_build_dir):
    return os.path.join(src_dir, '..', relative_build_dir)

def build_binary(user_target, build_dir, target_location, env, output_dir, output_name):
    cmake_target = user_target if user_target else 'all'
    cmake_build_cmd=f'time cmake --build {build_dir} --target {cmake_target}'
    print(cmake_build_cmd)
    subprocess.run(cmake_build_cmd, shell=True, env=env)
    built_bin = os.path.join(build_dir, target_location)
    out_bin = os.path.join(output_dir, output_name)
    print(f"Copying executable: {built_bin} -> {out_bin}")
    os.makedirs(output_dir, exist_ok=True)
    shutil.copy2(built_bin, out_bin)
    print(f"Binary executable saved to: {out_bin}")



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


