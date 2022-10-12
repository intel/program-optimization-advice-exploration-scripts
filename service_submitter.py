# Contributors: Yue, Cedric, Emmanuel
import os
import getpass
import datetime
from logger import log, QaasComponents

# Demo with preset values

SRC_URL='https://gitlab.com/davidwong/conv-codelets/-/archive/master/conv-codelets-master.tar.gz'
DATA_URL='https://gitlab.com/davidwong/conv-codelets/-/raw/master/nn-codelets/conv_op/direct_conv/1.1/1.1_back_prop_sx5/data.tar.gz'
DOCKER_FILE=''
OV_FILE=''

docker_file_content="""test 
is 
test
"""

def get_input(qaas_root):
    #qaas_user = os.getlogin()
    qaas_user = getpass.getuser()
    qaas_timestamp = int(round(datetime.datetime.now().timestamp()))
    service_dir = os.path.join(qaas_root, qaas_user, str(qaas_timestamp))
    os.makedirs(service_dir)
    docker_file=os.path.join(service_dir, 'Dockerfile')
    ov_file=os.path.join(service_dir, 'config.lua')
    return service_dir, SRC_URL, DATA_URL, docker_file, ov_file, qaas_timestamp
