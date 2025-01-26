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

import os
import sys
import subprocess
import cpuinfo
from utils.util import load_compiler_env

def get_hostname():
    '''Get the system hostname'''
    return os.uname()[1]

def get_ISA():
    '''Get the ISA'''
    return os.uname()[4]

def get_vendor_name():
    '''Get the CPU vendor ID'''
    vendor = cpuinfo.get_cpu_info()['vendor_id_raw']
    if vendor == 'GenuineIntel':
        return 'intel'
    elif vendor == 'AuthenticAMD':
        return 'amd'
    elif vendor == 'ARM':
        return 'arm'
    else:
        return 'unknown'

def get_family():
    '''Get the CPU family ID'''
    return cpuinfo.get_cpu_info()['family']

def get_model():
    '''Get the CPU model ID'''
    return cpuinfo.get_cpu_info()['model']

def get_model_name():
    '''Get the CPU model name'''
    try:
        return cpuinfo.get_cpu_info()['brand_raw']
    except:
        return "Unknown CPU model name"

def get_processor_name(maqao_dir, vendor):
    '''Get the Intel processor name'''
    if vendor == 'intel':
        return get_intel_processor_name(maqao_dir)
    elif vendor == 'amd':
        return get_amd_processor_name(maqao_dir)
    elif vendor == 'arm':
        return get_arm_processor_name(maqao_dir)
    else:
        return 'unknown'

def get_intel_processor_name(maqao_dir):
    '''Get the Intel processor name'''
    # Map from Micro-architure code from MAQAO detect-proc to short name used in intel.json
    # Default to OTHER if nothing is found.
    processor_name_dict = {
        "SAPPHIRE_RAPIDS":"SPR", # family == 6, model == 143
        "ICELAKE_SP":"ICL", # family == 6, model == 106
        "SKYLAKE":"SKX", # family == 6, model == 85
        "KABY_LAKE":"SKL", # family == 6, model == 158
        "HASWELL_E":"HSW",
        "HASWELL":"HSW", # family == 6, model == 63 or model == 79,
        "BROADWELL":"HSW"
    }
    proc_arch_name = get_processor_architecture(maqao_dir)
    return processor_name_dict.get(proc_arch_name, "OTHER")

def get_amd_processor_name(maqao_dir):
    '''Get the AMD processor name'''
    # Map from Micro-architure code from MAQAO detect-proc to short name used in intel.json
    # Default to OTHER if nothing is found.
    processor_name_dict = {
        "ZEN_V3":"ZEN3",
        "ZEN_V4":"ZEN4" #family == 25, model ==17
    }
    proc_arch_name = get_processor_architecture(maqao_dir)
    return processor_name_dict.get(proc_arch_name, "OTHER")

def get_arm_processor_name(maqao_dir):
    '''Get the ARM processor name'''
    # Map from Micro-architure code from MAQAO detect-proc to short name used in arm.json
    # Default to OTHER if nothing is found.
    processor_name_dict = {
        "ARM_NEOVERSE_V2":"NEOVERSE_V2",
        "ARM_NEOVERSE_V1":"NEOVERSE_V1",
        "ARM_NEOVERSE_N2":"NEOVERSE_N2",
        "ARM_NEOVERSE_N1":"NEOVERSE_N1"
    }
    proc_arch_name = get_processor_architecture(maqao_dir)
    return processor_name_dict.get(proc_arch_name, "OTHER")

def get_processor_architecture(maqao_dir):
    '''Get the processor architecture'''
    # Get the CPU code name
    parsed_output = get_mach_info_using_maqao(maqao_dir)
    return parsed_output['Micro-architecture code']

def get_mach_info_using_maqao(maqao_dir):
    try:
        output = subprocess.check_output([os.path.join(maqao_dir, 'bin', 'maqao'), "--detect-proc"], universal_newlines=True)
        parsed_output = { line.split(':', 1)[0].strip(): line.split(':',1)[1].strip() for line in output.split("\n") if line.strip()}
    except:
        parsed_output = {'Micro-architecture code': 'UNKNOWN_PROC'}
    return parsed_output

def get_number_of_cpus():
    '''Retrieve the number of logical CPUs from lscpu command'''
    count = int(subprocess.check_output('lscpu --extended=CPU | tail -n +2 | sort -u | wc -l', shell=True))
    return count

def get_number_of_cores():
    '''Retrieve the number of physical cores from lscpu command'''
    count = int(subprocess.check_output('lscpu --extended=CORE | tail -n +2 | sort -u | wc -l', shell=True))
    return count

def get_number_of_sockets():
    '''Retrieve the number of sockets from lscpu command'''
    count = int(subprocess.check_output('lscpu --extended=SOCKET | tail -n +2 | sort -u | wc -l', shell=True))
    return count

def get_number_of_nodes():
    '''Retrieve the number of sockets from lscpu command'''
    count = int(subprocess.check_output('lscpu --extended=NODE | tail -n +2 | sort -u | wc -l', shell=True))
    return count

def get_THP_policy():
    '''Retrieve the enforced transparent huge pages policy on the system'''
    return subprocess.check_output("grep -o '\[.*\]' /sys/kernel/mm/transparent_hugepage/enabled | cut -d'[' -f2 | cut -d']' -f1", shell=True).decode("utf-8").split('\n')[0]

def get_frequency_driver():
    '''Retrieve the frequency driver on the system'''
    try:
        return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver", shell=True).decode("utf-8").split('\n')[0]
    except:
        return "Unknown frequency driver"

def get_frequency_governor():
    '''Retrieve the frequency governor on the system'''
    try:
        return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", shell=True).decode("utf-8").split('\n')[0]
    except:
        return "Unknown frequency governor"

def get_scaling_max_frequency():
    '''Retrieve the scaling max frequency on the system'''
    try:
        return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq", shell=True).decode("utf-8").split('\n')[0]
    except:
        return "Unknown scaling max frequency"

def get_scaling_min_frequency():
    '''Retrieve the scaling min frequency on the system'''
    try:
        return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq", shell=True).decode("utf-8").split('\n')[0]
    except:
        return "Unknown scaling min frequency"

def get_scaling_cur_frequency():
    '''Retrieve the scaling current frequency on the system. Valid only for userspace governor provided by acpi-cpufreq driver'''
    try:
        return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed", shell=True).decode("utf-8").split('\n')[0]
    except:
        return "Unknown current frequency"

def get_advertized_frequency():
    '''Retrieve the advertized frequency on the system'''
    return "unsupported"

def get_maximal_frequency():
    '''Retrieve the maximal (Turbo) frequency on the system'''
    try:
        return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", shell=True).decode("utf-8").split('\n')[0]
    except:
        return "Unknown maximal frequency"

def get_compiler_version(compiler, compiler_dir):
    '''Get compiler version'''
    if compiler == "icx":
       cmd_version = "icx --version | head -n 1 | cut -d' ' -f6 | cut -d'(' -f2 | cut -d')' -f1"
    elif compiler == "icc":
       cmd_version = "icc  -diag-disable=10441  --version | head -n 1 | cut -d' ' -f3-4 | tr ' ' '.'"
    elif compiler == "gcc":
       cmd_version = "gcc --version | head -n 1 | cut -d')' -f2 | cut -d' ' -f2"
    elif compiler == "aocc":
       cmd_version = "clang --version | head -n 1 | grep -Po '(?<=AOCC_).*(?=-Build)'"
    elif compiler == "armclang":
       cmd_version = "armclang --version | head -n 1 | cut -d' ' -f5"
    else:
       cmd_version = ""
    try:
        env = load_compiler_env(compiler_dir)
        return subprocess.check_output(cmd_version, shell=True, env=env).decode("utf-8").split('\n')[0]
    except ImportError:
        return ""

def get_mpi_version(mpi_dir):
    '''Get MPI version'''
    cmdline = "mpirun --version | head -n 1"
    try:
        # Right now, still putting compilers and runtimes altogether.
        env = load_compiler_env(mpi_dir)
        output = subprocess.check_output(cmdline, shell=True, env=env).decode("utf-8").split('\n')[0]
    except ImportError:
        return ""
    # Check if MPI distribution is OpenMPI
    if output.find('Open MPI') != -1:
        return ('OpenMPI',f"{output.split(' ')[3]}")
    # Check if MPI distribution is IntelMPI
    elif output.find('') != -1:
        return ('IntelMPI',f"{output.split(' ')[7]}")
    return ('Unknown','NA')
