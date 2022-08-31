import datetime
import os
from logger import log, QaasComponents

def exec(binary, data_dir, ov_dir, ov_config, ov_result_root):
    ov_timestamp = int(round(datetime.datetime.now().timestamp()))
    ov_result_dir = os.path.join(ov_result_root, f'maqao_out_{ov_timestamp}')
    os.makedirs(ov_result_dir)
    log(QaasComponents.OV_RUNNER, f'OV run of {binary} for {data_dir} using {ov_dir} with configuration {ov_config}', mockup=True)
    log(QaasComponents.OV_RUNNER, f'Result at {ov_result_dir}', mockup=True)
    # MOCK create OV result dir
    return ov_result_dir
