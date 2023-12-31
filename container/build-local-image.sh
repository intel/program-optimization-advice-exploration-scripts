#!/bin/bash
# Build a local image for QaaS runs (trimmed down from CapeScripts version)
# By default production image will be used but can specify other tags.

ENABLE_DEVELOPMENT=1

tag_img=production
if [[ $# == 1 ]]; then
	tag_img="${1}"
fi
img_name=registry.gitlab.com/davidwong/qaas:${tag_img}
echo Base image name is: ${img_name}

# Ensure user logged in
local_gids=$(id -G)
local_gnames=$(id -Gn)

echo "Logging into registry.gitlab.com... (it may ask for gitlab.com password if not done before)"
docker login registry.gitlab.com
# Fetch latest image
docker pull ${img_name}

if [[ $http_proxy != http* ]]; then
  http_proxy_arg=http://${http_proxy}
else
  http_proxy_arg=${http_proxy}
fi

if [[ $https_proxy != http* ]]; then
  https_proxy_arg=http://${https_proxy}
else
  https_proxy_arg=${https_proxy}
fi

rm -f ssh.tar.gz
if [[ $ENABLE_DEVELOPMENT == "1" ]]; then
  tar cvfz ssh.tar.gz -C $HOME .ssh
else
  # Create empty dummy file to copy in
  touch ssh.tar.gz
fi

rm -rf cere
git clone git@github.com:benchmark-subsetting/cere.git --config core.autocrlf=input

echo -n "Enter Qaas user password:"
read -s QAAS_PASSWORD

docker build --build-arg IMG_NAME=${img_name} --build-arg http_proxy=$http_proxy_arg --build-arg https_proxy=$https_proxy_arg --build-arg LOCAL_UID=$(id -u ${USER}) --build-arg LOCAL_GID=$(id -g ${USER}) --build-arg LOCAL_GIDS="$local_gids" --build-arg LOCAL_GNAMES="$local_gnames" --build-arg ENABLE_DEVELOPMENT="$ENABLE_DEVELOPMENT" --build-arg QAAS_PASSWORD="$QAAS_PASSWORD" --pull --rm -f ./LocalDockerfile -t local_image_qaas .
