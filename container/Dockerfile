ARG BASE_IMAGE=ubuntu
ARG BASE_IMAGE_TAG=22.04

FROM ${BASE_IMAGE}:${BASE_IMAGE_TAG}

LABEL maintainer "Abdelhafid Mazouz abdelhafid.mazouz@intel.com>"
LABEL description="Base Image for running QaaS conatiners"

# Setup container environment work
RUN echo "alias ls='ls --color=auto'" >> /root/.bashrc && \
    echo "alias ll='ls -l'" >> /root/.bashrc; \
    apt-get update  && apt-get upgrade ; \
    apt-get install -y procps psmisc ; \
    apt-get install -y iputils-ping iproute2 wget ; \
    apt-get install -y git vim  ; \
    apt-get install -y pkg-config build-essential ; \
    apt-get install -y make gcc g++ gfortran cmake 

# Setup intel compiler
RUN export https_proxy=http://proxy-chain.intel.com:912 ; \
    wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /etc/apt/trusted.gpg.d/oneapi-archive-keyring.gpg > /dev/null ; \
    echo "deb https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list ; \
    apt-get update ; \
    apt-get install -y intel-oneapi-compiler-dpcpp-cpp-and-cpp-classic intel-oneapi-mkl intel-oneapi-mkl-devel intel-oneapi-mpi intel-oneapi-mpi-devel ; \
    mv /etc/apt/sources.list.d/oneAPI.list /etc/apt/sources.list.d/oneAPI.list.bak
