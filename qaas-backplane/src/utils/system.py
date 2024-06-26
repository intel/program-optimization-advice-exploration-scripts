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
    return cpuinfo.get_cpu_info()['brand_raw']

def get_intel_processor_name(maqao_dir):
    '''Get the processor name'''
    # Map from Micro-architure code from MAQAO detect-proc to short name used in intel.json
    # Default to OTHER if nothing is found.
    processor_name_dict = {
        "SAPPHIRE_RAPIDS":"SPR", "ICELAKE_SP":"ICL", "KABY_LAKE":"SKL",
        "SKYLAKE":"SKX", "HASWELL_E":"HSW", "HASWELL":"HSW" }
    proc_arch_name = get_processor_architecture(maqao_dir)
    return processor_name_dict.get(proc_arch_name, "OTHER")
    # family = get_family ()
    # # Get the CPU model ID
    # model = get_model()

    # if family == 6:
    #     if model == 143:
    #         CPU = 'SPR'
    #     elif model == 106:
    #         CPU = 'ICL'
    #     elif model == 85:
    #         CPU = 'SKL'
    #     # Should be Coffee Lake or Kaby Lake, but consider them SKL (needed for UVSQ "intel" machine)
    #     elif model == 158:
    #         CPU = 'SKL'
    #     elif model == 63 or model == 79:
    #         CPU = 'HSW'
    #     else:
    #         CPU = 'OTHER'

    # return CPU

def get_processor_architecture(maqao_dir):
    '''Get the processor architecture'''
    # Get the CPU code name
    parsed_output = get_mach_info_using_maqao(maqao_dir)
    return parsed_output['Micro-architecture code']

def get_mach_info_using_maqao(maqao_dir):
    output = subprocess.check_output([os.path.join(maqao_dir, 'bin', 'maqao'), "--detect-proc"], universal_newlines=True)
    parsed_output = { line.split(':', 1)[0].strip(): line.split(':',1)[1].strip() for line in output.split("\n") if line.strip()}
    return parsed_output
    # CPU =  get_intel_processor_name()

    # # Translate CPU name into architecture code
    # if CPU == 'SPR':
    #     architecture = 'SAPPHIRE_RAPIDS'
    # elif CPU == 'ICL':
    #     architecture = 'ICELAKE_SP'
    # elif CPU == 'SKL':
    #     architecture = 'SKYLAKE'
    # else:
    #     architecture = ''

    # return architecture

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
    return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver", shell=True).decode("utf-8").split('\n')[0]

def get_frequency_governor():
    '''Retrieve the frequency governor on the system'''
    return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor", shell=True).decode("utf-8").split('\n')[0]

def get_scaling_max_frequency():
    '''Retrieve the scaling max frequency on the system'''
    return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq", shell=True).decode("utf-8").split('\n')[0]

def get_scaling_min_frequency():
    '''Retrieve the scaling min frequency on the system'''
    return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq", shell=True).decode("utf-8").split('\n')[0]

def get_advertized_frequency():
    '''Retrieve the advertized frequency on the system'''
    return "unsupported"

def get_maximal_frequency():
    '''Retrieve the maximal (Turbo) frequency on the system'''
    return subprocess.check_output("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", shell=True).decode("utf-8").split('\n')[0]

def get_compiler_version(compiler, compiler_dir):
    '''Get compiler version'''
    if compiler == "icx":
       cmd_version = "icx --version | head -n 1 | cut -d' ' -f6 | cut -d'(' -f2 | cut -d')' -f1"
    elif compiler == "icc":
       cmd_version = "icc  -diag-disable=10441  --version | head -n 1 | cut -d' ' -f3-4 | tr ' ' '.'"
    elif compiler == "gcc":
       cmd_version = "gcc --version | head -n 1 | cut -d' ' -f4"
    try:
        env = load_compiler_env(compiler_dir)
        return subprocess.check_output(cmd_version, shell=True, env=env).decode("utf-8").split('\n')[0]
    except ImportError:
        return ""
