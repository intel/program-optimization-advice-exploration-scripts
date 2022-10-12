# Contributors: Yue, Cedric, Emmanuel
import os
import getpass
import datetime
from logger import log, QaasComponents

# Demo with preset values

SRC_URL='https://gitlab.com/davidwong/conv-codelets/-/archive/master/conv-codelets.tar.gz'
DATA_URL='https://gitlab.com/davidwong/conv-codelets/-/raw/master/nn-codelets/conv_op/direct_conv/1.1/1.1_back_prop_sx5/data.tar.gz'
DOCKER_FILE=''
OV_FILE=''

docker_file_content="""test 
is 
test
"""

MOCK_UP_USER_CC='icc'
MOCK_UP_USER_C_FLAGS='-g -qno-offload -fpic -wd266 -diag-disable 1879,3415,10006,10010,10411,13003 -O3 -fno-alias -ansi-alias -qoverride_limits -fp-model fast=2 -D_REENTRANT -xCore-AVX512 -qopt-zmm-usage=high'
MOCK_UP_USER_CXX_FLAGS=''
MOCK_UP_USER_FC_FLAGS=''
MOCK_UP_USER_LINK_FLAGS='-g -fpic -diag-disable 1879,3415,10006,10010,10411 -Wl,--as-needed -lrt -ldl -Wl,--no-as-needed -Wl,--as-needed -lstdc++ -Wl,--no-as-needed'
MOCK_UP_USER_TARGET='1.1_back_prop_sx5'

def get_input(qaas_root):
    #qaas_user = os.getlogin()
    qaas_user = getpass.getuser()
    qaas_timestamp = int(round(datetime.datetime.now().timestamp()))
    service_dir = os.path.join(qaas_root, qaas_user, str(qaas_timestamp))
    os.makedirs(service_dir)
    docker_file=os.path.join(service_dir, 'Dockerfile')
    ov_file=os.path.join(service_dir, 'config.lua')
    return service_dir, SRC_URL, DATA_URL, docker_file, ov_file, qaas_timestamp, \
        MOCK_UP_USER_CC, MOCK_UP_USER_C_FLAGS, MOCK_UP_USER_CXX_FLAGS, MOCK_UP_USER_FC_FLAGS, \
            MOCK_UP_USER_LINK_FLAGS, MOCK_UP_USER_TARGET


