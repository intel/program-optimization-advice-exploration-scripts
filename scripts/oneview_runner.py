# Contributors: Cedric/Emmanuel
import datetime
import os
from logger import log, QaasComponents
import subprocess
import pandas as pd
import argparse
from util import generate_timestamp_str

script_dir=os.path.dirname(os.path.realpath(__file__))
SRC_INFO_LUA_FILE=os.path.join(script_dir, 'src_tree.lua')

# TODO: integrate back to qaas script
MAQAO_CSV_SEP = ';'
#ONEVIEW_DIR="/nfs/site/proj/alac/software/UvsqTools/20221028"
ONEVIEW_DIR="/nfs/site/proj/alac/software/UvsqTools/20221102"
ONEVIEW_LIB=os.path.join(ONEVIEW_DIR, 'lib')
ONEVIEW_BIN=os.path.join(ONEVIEW_DIR, 'bin')
MAQAO_BIN=os.path.join(ONEVIEW_BIN, 'maqao')

# Variable names in LProf results
LPROF_LOOP_PATH_VAR = 'Loop Path'
LPROF_TIME_METRIC = 'Time w.r.t Walltime (s)'
LPROF_MIN_CYCLES_METRIC = 'ref-cycles min events'
LPROF_MAX_CYCLES_METRIC = 'ref-cycles max events'
LPROF_AVG_CYCLES_METRIC = 'ref-cycles avg events'

LPROF_OUT_DIR='lprof_out_dir'
LPROF_OUT_CSV=os.path.join(LPROF_OUT_DIR, 'csv', 'lprof_loops_cluster_Cluster.csv')

def aggregate_loop_time(run_dir, binary, src_file, loop_head_line_num):
    my_env = os.environ.copy()
    loop_profile = parse_lprof_loop_profile(my_env, run_dir, binary)
    # Add up time if <src_file>:<loop_head_line_num> show up in loop path
    matchedMask = loop_profile['Loop Path'].apply(lambda lpath: f'{src_file}:{loop_head_line_num}' in lpath)
    # return cycle counts (min of 1)
    return max(1, loop_profile.loc[matchedMask,LPROF_AVG_CYCLES_METRIC].sum().item()), LPROF_AVG_CYCLES_METRIC

def run_lprof_loop_profile(run_dir, my_env, run_cmd, binary_name):

    true_run_cmd = run_cmd.replace('<binary>', './'+binary_name)
    # First rename the old lprof directory if exists
    rename_dir_name=f'{LPROF_OUT_DIR}-{generate_timestamp_str()}'
    old_dir = os.path.join(run_dir, LPROF_OUT_DIR)
    if os.path.exists(old_dir):
        os.rename(old_dir, os.path.join(run_dir, rename_dir_name))
    true_run_cmd=f'{MAQAO_BIN} lprof -dl xp={LPROF_OUT_DIR} -- {true_run_cmd}'
    subprocess.run(true_run_cmd, shell=True, env=my_env, cwd=run_dir)

def parse_lprof_loop_profile(my_env, run_dir, binary):
    true_run_cmd = f'{MAQAO_BIN} lprof --show-full-paths --display-raw-events=events -dl -of=csv xp={LPROF_OUT_DIR}'
    subprocess.run(true_run_cmd, shell=True, env=my_env, cwd=run_dir)
    profile_df = pd.read_csv(os.path.join(run_dir, LPROF_OUT_CSV), sep=MAQAO_CSV_SEP)
    profile_df[LPROF_LOOP_PATH_VAR] = None
    for index, row in profile_df.iterrows():
        loop_id = row['Loop ID']
        src_info_run_cmd = f'{MAQAO_BIN} {SRC_INFO_LUA_FILE} {binary} {loop_id}' 
        results = subprocess.run(src_info_run_cmd, shell=True, env=my_env, cwd=run_dir, capture_output=True, encoding='UTF-8')
        results = results.stdout.strip().split(' <- ')
        fun = results.pop(0)
        # results now has the loop path
        profile_df.at[index, LPROF_LOOP_PATH_VAR] = results

    profile_df[LPROF_AVG_CYCLES_METRIC] = (profile_df[LPROF_MIN_CYCLES_METRIC] + profile_df[LPROF_MAX_CYCLES_METRIC])/2
    return profile_df

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
