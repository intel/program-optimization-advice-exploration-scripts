import pandas as pd
import configparser
import zlib
import hashlib
import os
import numpy as np
def read_file(path, delimiter=';'):
    df = pd.read_csv(path, sep=delimiter, keep_default_na=False, index_col=False, skipinitialspace=True, na_values=[''])
    df = df.replace({np.nan: None})
    return df


def get_config():
    SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH=os.path.join(SCRIPT_DIR, "..", '..',"config", "qaas-web.conf")
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read(CONFIG_PATH)
    return config

def compress_file(filename):
    with open(filename, 'rb') as f:
        content = f.read()
    return zlib.compress(content, 9)

def get_file_sha256(filename):
    with open(filename, 'rb') as f:
        sha256_hash = hashlib.sha256(f.read()).hexdigest()
    return sha256_hash
def decompress_file(compressed_content):
    return zlib.decompress(compressed_content)