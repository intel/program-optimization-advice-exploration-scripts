#!/bin/bash


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

#script_dir=$(dirname $0)
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
    env_args+=("-e $var=${!var}")
  fi
done


#docker run --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /usr/src/linux-headers-$(uname -r):/usr/src/linux-headers-$(uname -r) -v /lib/modules:/lib/modules -v /usr/src/linux-headers-4.4.0-62:/usr/src/linux-headers-4.4.0-62 -v /tmp/tmp:/tmp/tmp -v /dev:/dev -v /usr/include:/usr/include --pid=host --ipc=host -w /host/$(pwd) -it --privileged local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --cap-add=all -it local_image_qaas:latest 
#docker run --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=unconfined -it local_image_qaas:latest 
docker volume create mysql_data
docker volume create letsencrypt_data
docker volume create mods_enabled_data
docker volume create htpasswd_data

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

#docker run -p 81:80  --hostname $(hostname) --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
# docker run --user root -p 81:80 --restart unless-stopped --entrypoint /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
# docker run --user root -p 81:80 --restart on-failure:1 --entrypoint /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
#docker run --user root -p 81:80 --restart unless-stopped --entrypoint /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest 
# use entrypoint.sh script to wrap various restart command.  The script will end with "su qaas" to start an interactive shell without quitting as qaas user.
docker run --user root -p 80:80 -p 443:443 -p 3000:3000 --restart unless-stopped  --hostname $(hostname) ${mount_args[*]} ${env_args[*]} -v /:/host -v mysql_data:/var/lib/mysql -v letsencrypt_data:/etc/letsencrypt -v mods_enabled_data:/etc/apache2/mods-enabled -v htpasswd_data:/etc/apache2/auth -v /lib/modules:/lib/modules -v /tmp/tmp:/tmp/tmp -v /dev:/dev --pid=host --ipc=host -w /host/$(pwd) --security-opt seccomp=./qaas-docker-seccomp-profile.json -it local_image_qaas:latest /host/$SCRIPT_DIR/../qaas-web/deployment/entrypoint.sh

#container_id=$(docker run --rm  ${mount_args[*]} ${env_args[*]} -v /:/host -v /usr/src/linux-headers-$(uname -r):/usr/src/linux-headers-$(uname -r) -v /lib/modules:/lib/modules -v /usr/src/linux-headers-4.4.0-62:/usr/src/linux-headers-4.4.0-62 -v /tmp/tmp:/tmp/tmp -v /dev:/dev -v /usr/include:/usr/include --pid=host --ipc=host -d -it --privileged local_image_qaas:latest )
# Run as root to start EMON driver.  Simply give access to docker group
#docker exec -u 0 ${container_id} sh -c "/opt/intel/sep_eng/sepdk/src/insmod-sep -g docker"

#docker attach ${container_id}
#docker exec -u 0 ${container_id} sh -c "/opt/intel/sep_eng/sepdk/src/rmmod-sep"
