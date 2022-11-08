# Contributors: Cedric/Emmanuel
import datetime
import os
from logger import log, QaasComponents
import argparse
from util import generate_timestamp_str
script_dir=os.path.dirname(os.path.realpath(__file__))
# SRC_INFO_LUA_FILE=os.path.join(script_dir, 'src_tree.lua')

# # TODO: integrate back to qaas script
# MAQAO_CSV_SEP = ';'
# #ONEVIEW_DIR="/nfs/site/proj/alac/software/UvsqTools/20221028"
# ONEVIEW_DIR="/nfs/site/proj/alac/software/UvsqTools/20221102"
# ONEVIEW_LIB=os.path.join(ONEVIEW_DIR, 'lib')
# ONEVIEW_BIN=os.path.join(ONEVIEW_DIR, 'bin')
# MAQAO_BIN=os.path.join(ONEVIEW_BIN, 'maqao')


# LPROF_OUT_DIR='lprof_out_dir'
# LPROF_OUT_CSV=os.path.join(LPROF_OUT_DIR, 'csv', 'lprof_loops_cluster_Cluster.csv')


def exec(binary, data_dir, ov_dir, ov_config, ov_result_root):
    ov_timestamp = int(round(datetime.datetime.now().timestamp()))
    ov_result_dir = os.path.join(ov_result_root, f'maqao_out_{ov_timestamp}')
    os.makedirs(ov_result_dir)
    log(QaasComponents.OV_RUNNER, f'OV run of {binary} for {data_dir} using {ov_dir} with configuration {ov_config}', mockup=True)
    log(QaasComponents.OV_RUNNER, f'Result at {ov_result_dir}', mockup=True)
    # MOCK create OV result dir
    return ov_result_dir

def main():
    parser = argparse.ArgumentParser(description="Testing loop time aggregation")
    parser.add_argument('--run-path', help='Path to run directory', required=True)
    parser.add_argument('--binary-path', help='Path to executable binary', required=True)
    parser.add_argument('--src-file', help='Loop source file', required=True)
    parser.add_argument('--loop-line-num', help='Loop head line number', required=True, type=int)
    args = parser.parse_args()
    time_result, unit_result = aggregate_loop_time(args.run_path, args.binary_path, args.src_file, args.loop_line_num)
    pass

if __name__ == "__main__": 
    main()
