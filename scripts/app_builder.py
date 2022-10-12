# Contributors: David/Jeongnim
import os
from logger import log, QaasComponents


def exec(src_dir, compiler_dir, relative_binary_path):
    log(QaasComponents.APP_BUILDER, f'Building binary to be compiled by {compiler_dir}', mockup=True)
    orig_binary = os.path.join(src_dir, relative_binary_path)
    log(QaasComponents.APP_BUILDER, f'Output to binary {orig_binary}', mockup=True)
    return orig_binary