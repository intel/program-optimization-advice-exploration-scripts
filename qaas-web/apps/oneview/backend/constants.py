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

EXECUTION_METRIC_TYPES = [
                    'total_time', 'array_access_efficiency', 'profiled_time',
                    'number_of_cores', 'speedup_if_clean',
                    'speedup_if_fp_vect', 'speedup_if_fully_vectorised',
                    'speedup_if_FP_only', 'model_name',
                    'time_in_analyzed_loops', 'time_in_analyzed_innermost_loops',
                    'time_in_user_code', 'compilation_options_score',
                    'perfect_flow_complexity', 'perfect_openmp_mpi_pthread',
                    'perfect_openmp_mpi_pthread_load_distribution','compilation_flags',
                    'iterations_count', 'program','experiment_name'
                ]

CQA_LOOP_METRIC_TYPES = [
    'vectorization_ratio', 'vectorization_efficiency'

]

