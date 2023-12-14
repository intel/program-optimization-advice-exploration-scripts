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
# Contributors: Yue/David
dyn_cntr = [
    "INST_RETIRED_ANY",
    "CPU_CLK_UNHALTED_THREAD",
    "UNC_IMC_DRAM_DATA_READS",
    "UNC_IMC_DRAM_DATA_WRITES",
    "L1D_REPLACEMENT",
    "L2_DEMAND_RQSTS_WB_HIT",
    "L2_TRANS_L1D_WB",
    "L2_LINES_IN_ALL",
    "L2_TRANS_L2_WB",
    "L2_RQSTS_MISS",
    "L2_DEMAND_RQSTS_WB_MISS",
    "MEM_LOAD_UOPS_RETIRED_L1_MISS_PS",
    "MEM_LOAD_UOPS_RETIRED_L1_HIT_PS",
    "MEM_LOAD_UOPS_RETIRED_L2_HIT_PS",
    "MEM_LOAD_UOPS_RETIRED_HIT_LFB",
    "MEM_LOAD_UOPS_RETIRED_L3_HIT_PS",
    "MEM_LOAD_UOPS_RETIRED_L3_MISS",
    "L1D_PEND_MISS_PENDING",
    "L1D_PEND_MISS_PENDING_CYCLES",
    "DTLB_LOAD_MISSES_MISS_CAUSES_A_WALK",
    "DTLB_LOAD_MISSES_STLB_HIT",
    "DTLB_STORE_MISSES_MISS_CAUSES_A_WALK",
    "DTLB_STORE_MISSES_STLB_HIT",
    "DTLB_LOAD_MISSES_WALK_DURATION",
    "DTLB_STORE_MISSES_WALK_DURATION",
    "RESOURCE_STALLS_ANY",
    "RESOURCE_STALLS_RS",
    "RESOURCE_STALLS_LB",
    "RESOURCE_STALLS_SB",
    "RESOURCE_STALLS_OOO_RSRC",
    "RESOURCE_STALLS2_ALL_PRF_CONTROL",
    "RESOURCE_STALLS_ROB",
    "RESOURCE_STALLS_MEM_RS",
    "RESOURCE_STALLS_LB_SB",
    "RESOURCE_STALLS_OTHER",
    "RESOURCE_STALLS_LOAD_MATRIX",
    "RESOURCE_STALLS2_PHT_FULL",
    "RESOURCE_STALLS_FPCW_OR_MXCSR",
    "L2_RQSTS_L2_PF_MISS",
    "L2_RQSTS_L2_PF_HIT",
    "L2_RQSTS_ALL_PF",
    "LOAD_HIT_PRE_SW_PF",
    "MSR_DRAM_ENERGY_STATUS",
    "MSR_PP0_ENERGY_STATUS",
    "MSR_PKG_ENEGY_STATUS",
    "MSR_RAPL_POWER_UNIT"
]
derived_metrics = [
    "L2RWRate",
    "RAMRWRate",
    "AveRequestInFlight",
    "RSUtil",
    "LBUtil",
    "SBUtil",
    "ROBUtil",
    "PRFUtil",
    "LMUtil",
    "InstRate",
    "AllHit",
    "%L1Hit",
    f"%LfbHit",
    "%L2Hit",
    "%L3Hit",
    "%L3Miss",
    "TlbHit",
    "TlbDuration",
    "MLP"
]
inst_cnt = [
    "inst_cnt",
    "scalar_ld_cnt",
    "vector_ld_cnt",
    "scalar_st_cnt",
    "vector_st_cnt",
    "fp_arith_inst_cnt",
    "fp_sse_inst_cnt",
    "fp_avx_inst_cnt",
    "int_sse_inst_cnt",
    "int_avx_inst_cnt",
    "vector_inst_exclude_mem_cnt",
    "vector_other_inst_cnt"
]


compiler_flags = ['base', 'novec', 'sse', 'avx', 'avx2']


