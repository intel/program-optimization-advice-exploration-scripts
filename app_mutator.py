# Contributors: Padua/Yoonseo
import os
from logger import log, QaasComponents

def exec(src_dir, compiler_dir, relative_binary_path):
    log(QaasComponents.APP_MUTATOR, f'Tuning source code from {src_dir} to be compiled by {compiler_dir}', mockup=True)
    opt_binary = os.path.join(src_dir, relative_binary_path)
    log(QaasComponents.APP_MUTATOR, f'Output to Optimized binary {opt_binary}', mockup=True)
    return opt_binary