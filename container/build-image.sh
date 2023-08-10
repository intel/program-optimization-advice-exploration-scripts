#!/bin/bash
# Trimmed down version from https://gitlab.com/davidwong/cape-experiment-scripts/-/blob/master/container/build-image.sh

push_image=false
while getopts ":p" opt; do
  case ${opt} in
  p)
    push_image=true
    ;;
  \?)
    echo "Usage: $0 [-p]"
    exit
    ;;
  esac
done

#rm -rf rose-utils
#mkdir -p rose-utils
#pushd rose-utils
# User the image builder's .ssh
if [ ! -d rose-utils-for-qaas ]; then
  git clone https://gitlab.com/davidwong/rose-utils-for-qaas.git --config core.autocrlf=input
#popd
fi

if [ ! -d ice-locus-dev ]; then
  git clone https://bitbucket.org/thiagotei/ice-locus-dev.git  --config core.autocrlf=input
  cd ice-locus-dev
  git checkout intel
  cd ..
fi

if [ ! -d fdo-lib ]; then
  git clone git@gitlab.com:davidwong/fdo-lib.git
fi

if [ ! -d cere ]; then
  git clone git@github.com:david-c-wong/cere.git --config core.autocrlf=input
  cd cere
  git checkout multi-codelet-capture
  cd ..
fi


if [ ! -d pocc-1.1 ]; then
  curl -O http://web.cs.ucla.edu/~pouchet/software/pocc/download/pocc-1.1-full.tar.gz
  tar xvf pocc-1.1-full.tar.gz
  cd pocc-1.1
  curl -O https://bitbucket.org/thiagotei/uiuc-compiler-opts/raw/39556c88b86e6a7e727117183c93906ab89ffeb1/pocc-1.1-candl-0.6.2.patch
  cd ..
fi

if [ ! -d uiuc-compiler-opts ]; then
  git clone https://bitbucket.org/thiagotei/uiuc-compiler-opts.git --config core.autocrlf=input
fi

cp ../scripts/app_runner.py .
cp ../qaas-service/app_builder.py .

#docker build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy --pull --rm -f "container\Dockerfile" -t capeexperimentscripts:latest "container"
# Below assums proxy servers are needed to access the network
#docker build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy --pull --rm -f ".\Dockerfile" -t capeexperimentscripts:latest "."

# login only need to be done once for password entering
docker login registry.gitlab.com
# Also build the image to Gitlab
[[ $http_proxy != http://* ]] && http_proxy=http://$http_proxy
[[ $https_proxy != http://* ]] && https_proxy=http://$https_proxy
pwd
docker build --build-arg http_proxy=$http_proxy --build-arg https_proxy=$https_proxy --pull --rm -f "./Dockerfile" -t registry.gitlab.com/davidwong/qaas:development  "."
exit 0

# TODO: delete this with other scripts being used to push and tag images
if [[ $push_image = true ]]; then
  docker push registry.gitlab.com/davidwong/qaas
fi
