#!/bin/bash

# Script for Container running 
#
# Usage: run-container.sh [-r] [-s] [-p] [<script>]
#
# -r specify whether we want the container to restart
#   with -r, restart policy=unless-stopped, otherwise policy=no
# -d specify whether we want the container to run detached 
#   with -d, container will be run as detached mode (-d)
#   without it, container will be run as default 
# -p specify whether we want to run the container with privileged user
#   with -p, will run as root, otherwise will run as qaas
#
# User can provide optional script to run inside the container
# If script is provided,
#   If an existing container is running, run the script in that container
#   If no existing container running, create container and run the script. 
# If no script is provided, run container as terminal
#   if an existing container is running, run with "exec" -it flag
#   If no existing container running, run with "run" -it flag 
#     (The idea of entrypoint.sh is like a boot up script. TODO: ensure component 
#      specific code, may be split into different QaaS folders )

QAAS_CONTAINER_NAME=qaas_container
restart_policy=no
detached_cmd=
container_user=qaas

# Check if the container is running
QAAS_CONTAINER_RUNNING=0
if docker ps --filter "name=${QAAS_CONTAINER_NAME}" --format '{{.Names}}' | grep -q "${QAAS_CONTAINER_NAME}"; then
  QAAS_CONTAINER_RUNNING=1
fi

while getopts ":rdp" opt; do
 case ${opt} in
 r)
   restart_policy=unless-stopped
   ;;
 d)
   detached_cmd=-d
   ;;
 p)
   container_user=root
   ;;
 \?)
   echo "Usage: $0 [-r] [-s] <more commands, including scripts>"
   exit
   ;;
 esac
done
shift $((OPTIND-1))

echo "Restart policy: ${restart_policy}"



#while getopts ":n" opt; do
#  case ${opt} in
#  \?)
#    echo "Usage: $0 [-n]"
#    exit
#    ;;
#  esac
#done

# Fetch latest image
#docker pull registry.gitlab.com/davidwong/cape-experiment-scripts:latest

script_dir=$(dirname $0)
#root_dir=$(readlink -f ${script_dir}/..)
#docker run --rm  -v ${root_dir}:/home/appuser/cape-experiment-scripts -it registry.gitlab.com/davidwong/cape-experiment-scripts:latest
#docker run --rm  -v ${root_dir}:/home/appuser/cape-experiment-scripts -it local_image_qaas:latest
#docker run --rm  -v /nfs:/nfs -v /opt:/opt -v /localdisk:/localdisk -v /:/host -it local_image_qaas:latest
#docker run --rm  -v /nfs:/nfs -v /opt:/opt -v /localdisk:/localdisk -v /:/host -it --privileged local_image_qaas:latest
#docker run --rm  -v /opt:/opt -v /localdisk:/localdisk -v /:/host -it --privileged local_image_qaas:latest

# Build arguments to mount host directories
mount_args=()
mount_dirs=(/opt /localdisk /nfs)
mount_dirs=(/localdisk )
nfs_mount_dirs=(/nfs)
for dir in ${mount_dirs[*]}; do
    mount_args+=( "-v $dir:$dir" )
done
for dir in ${nfs_mount_dirs[*]}; do
    mount_args+=( "-v $dir:$dir:shared" )
done
#mount_args+=( "-v $HOME:/home/runner" )

# Build arguments to pass environmental variables
env_args=()
vars=(http_proxy https_proxy)
for var in ${vars[*]}; do
  if [[ ! -z ${!var} ]]; then
    var_value=${!var}
    env_args+=("-e $var=${var_value}")
  fi
done


#docker run --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /usr/src/linux-headers-$(uname -r):/usr/src/linux-headers-$(uname -r) -v /lib/modules:/lib/modules -v /usr/src/linux-headers-4.4.0-62:/usr/src/linux-headers-4.4.0-62 -v /tmp/tmp:/tmp/tmp -v /dev:/dev -v /usr/include:/usr/include --pid=host --ipc=host -w /host/$(pwd) -it --privileged local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --cap-add=all -it local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=unconfined -it local_image_qaas:latest 

# Following volumes will be initialized when qaas-web/setup.sh is run, 
# which would trigger install.py and update_web.py scripts
docker volume create mysql_data  #initialized in qaas-web/deployment/install.py (when vol is empty)
docker volume create letsencrypt_data # initialized by user
docker volume create mods_enabled_data # initialized by user
docker volume create htpasswd_data # initialized in qaas-web/setup.sh
docker volume create www_html_data # initialized in qaas-web/deployment/update_web.py (when vol is empty)
docker volume create apache2_site_conf # initialized in qaas-web/setup.sh

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
# DEPLOY_DIR=/host/$SCRIPT_DIR/../qaas-web/deployment
setup_script_path=/host$SCRIPT_DIR/../setup.sh

echo "run setup.sh in run container.sh ${setup_script_path}  ${USER} $#"
if [[ $# == 0 ]]; then
  #docker_run_cmd=(-it local_image_qaas:latest )
  # docker_run_cmd=(-it local_image_qaas:latest ${DEPLOY_DIR}/entrypoint.sh)
  # command_to_run="bash ${setup_script_path}"
  docker_run_cmd=(-it local_image_qaas:latest ${setup_script_path})

else
  docker_run_cmd=(local_image_qaas:latest $*)
fi

if [[ $QAAS_CONTAINER_RUNNING == 0 ]]; then
  echo "Terminal with run command"

  docker_run_cmd=(-it local_image_qaas:latest $*)

  docker container rm ${QAAS_CONTAINER_NAME} 2>/dev/null
  docker run --user ${container_user} -p 8080:80 -p 443:443 -p 3000:3000 --restart ${restart_policy}  \
    --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v apache2_site_conf:/etc/apache2/sites-available -v mysql_data:/var/lib/mysql -v letsencrypt_data:/etc/letsencrypt -v mods_enabled_data:/etc/apache2/mods-enabled \
    -v htpasswd_data:/etc/apache2/auth -v www_html_data:/var/www/html -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) \
    ${detached_cmd} --name ${QAAS_CONTAINER_NAME} \
    --security-opt seccomp=${script_dir}/qaas-docker-seccomp-profile.json ${docker_run_cmd[*]}
else
  echo "Terminal with exec command"
  docker_run_cmd=(-it ${QAAS_CONTAINER_NAME} /bin/bash $*)
  docker exec --user ${container_user} ${env_args[*]} -w /host/$(pwd) ${docker_run_cmd[*]}
fi



exit

#docker run --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /usr/src/linux-headers-$(uname -r):/usr/src/linux-headers-$(uname -r) -v /lib/modules:/lib/modules -v /usr/src/linux-headers-4.4.0-62:/usr/src/linux-headers-4.4.0-62 -v /tmp/tmp:/tmp/tmp -v /dev:/dev -v /usr/include:/usr/include --pid=host --ipc=host -w /host/$(pwd) -it --privileged local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --cap-add=all -it local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=unconfined -it local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=${script_dir}/qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
#docker run -p 81:80  --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
# docker run --user root -p 81:80 --restart unless-stopped --entrypoint /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
# docker run --user root -p 81:80 --restart on-failure:1 --entrypoint /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
#docker run --user root -p 81:80 --restart unless-stopped --entrypoint /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
# use entrypoint.sh script to wrap various restart command.  The script will end with "su qaas" to start an interactive shell without quitting as qaas user.
docker run --user root -p 8080:80 -p 443:443 -p 3000:3000 --restart unless-stopped  \
  --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v letsencrypt_data:/etc/letsencrypt -v mods_enabled_data:/etc/apache2/mods-enabled \
  -v htpasswd_data:/etc/apache2/auth -v www_html_data:/var/www/html -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) \
  --name ${QAAS_CONTAINER_NAME} \
  --security-opt seccomp=${script_dir}/qaas-docker-seccomp-profile.json ${docker_run_cmd[*]}


#container_id=$(docker run --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /usr/src/linux-headers-$(uname -r):/usr/src/linux-headers-$(uname -r) -v /lib/modules:/lib/modules -v /usr/src/linux-headers-4.4.0-62:/usr/src/linux-headers-4.4.0-62 -v /tmp/tmp:/tmp/tmp -v /dev:/dev -v /usr/include:/usr/include --pid=host --ipc=host -d -it --privileged local_image_qaas:latest )
# Run as root to start EMON driver.  Simply give access to docker group
#docker exec -u 0 ${container_id} sh -c "/opt/intel/sep_eng/sepdk/src/insmod-sep -g docker"

#docker attach ${container_id}
#docker exec -u 0 ${container_id} sh -c "/opt/intel/sep_eng/sepdk/src/rmmod-sep"
