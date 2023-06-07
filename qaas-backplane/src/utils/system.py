# Contributors: Hafid/David
import os
import sys
import cpuinfo

def get_vendor_name():
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

def get_intel_processor_name():
    # Get the CPU family ID
    family = get_family ()
    # Get the CPU model ID
    model = get_model()

    if family == 6:
        if model == 143:
            CPU = 'SPR'
        if model == 106:
            CPU = 'ICX'
        elif model == 63 or model == 79:
            CPU = 'HSW'
        else:
            CPU = 'OTHER'

    return CPU

