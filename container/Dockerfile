ARG BASE_IMAGE=ubuntu
ARG BASE_IMAGE_TAG=22.04

FROM ${BASE_IMAGE}:${BASE_IMAGE_TAG}

LABEL maintainer "Abdelhafid Mazouz abdelhafid.mazouz@intel.com>"
LABEL description="Base Image for running QaaS conatiners"

# # Setup container environment work
# RUN echo "alias ls='ls --color=auto'" >> /root/.bashrc && \
#     echo "alias ll='ls -l'" >> /root/.bashrc; \
#     apt-get update  && apt-get upgrade ; \
#     apt-get install -y procps psmisc ; \
#     apt-get install -y iputils-ping iproute2 wget ; \
#     apt-get install -y git vim  ; \
#     apt-get install -y pkg-config build-essential ; \
#     apt-get install -y make gcc g++ gfortran cmake 

# # Setup intel compiler
# RUN export https_proxy=http://proxy-chain.intel.com:912 ; \
#     wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /etc/apt/trusted.gpg.d/oneapi-archive-keyring.gpg > /dev/null ; \
#     echo "deb https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list ; \
#     apt-get update ; \
#     apt-get install -y intel-oneapi-compiler-dpcpp-cpp-and-cpp-classic intel-oneapi-mkl intel-oneapi-mkl-devel intel-oneapi-mpi intel-oneapi-mpi-devel ; \
#     mv /etc/apt/sources.list.d/oneAPI.list /etc/apt/sources.list.d/oneAPI.list.bak

# Need to install gcc-4.9 
# See https://askubuntu.com/questions/1235819/ubuntu-20-04-gcc-version-lower-than-gcc-7
RUN echo "deb http://dk.archive.ubuntu.com/ubuntu/ xenial main" >> /etc/apt/sources.list && echo "deb http://dk.archive.ubuntu.com/ubuntu/ xenial universe" >> /etc/apt/sources.list

RUN apt-get update && apt-get install --no-install-recommends -y make \
 software-properties-common && \
 add-apt-repository ppa:rosecompiler/rose-development && \
 apt-get update && apt-get install --no-install-recommends -y g++ rsync zip openssh-server \
# Following steps from ROSE website: https://github.com/rose-compiler/rose/wiki/Install-Using-apt-get
   rose \
 # Optional: Installs ROSE tools in addition to ROSE Core
   rose-tools \
# More utilities specified at https://gitlab.com/Wingpad/rose-utils
   default-jdk \
   git git-lfs g++ wget \
# More basic utilities
   vim \
   less \
   sudo \
 # Need pkg-config to csvkit
   pkg-config \
 # Used in Capescripts
   bc \
   time \
   python3-pip \
   cpufrequtils numactl \
# For Locus
   lib32readline8 lib32readline-dev \
   cproto ctags build-essential libreadline-dev libncurses5-dev \
   libncursesw5-dev \
   subversion python-is-python3 \
   indent swig \
   # for pocc, need to install gcc-4.9 
   gcc-4.9 g++-4.9 uuid-dev libswitch-perl \
   # for hugeadm
   libhugetlbfs-bin \
   # for new build of cmake
   libssl-dev \
   # for UIUC Compiler Optimizations
   libgmp-dev \
   # for LORE mutator in UIUC Compiler Optimizations
   gcc-8 g++-8 \
   # for PROMPT
   binutils-dev libiberty-dev

 #tex4ht
 #texlive-latex-base texlive-latex-extra 


RUN chmod u+s /usr/bin/cpufreq-set

RUN python3 -m pip install sympy \
  && python3 -m pip install csvkit \
  && python3 -m pip install openpyxl \
  && python3 -m pip install et_xmlfile \
  && python3 -m pip install Cheetah3 \
  && python3 -m pip install parse \
  && python3 -m pip install pandas


# configure SSH for communication with Visual Studio 
RUN mkdir -p /var/run/sshd

RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config && \ 
   ssh-keygen -A 

# expose port 22 
EXPOSE 22

# Build cmake
RUN cd /root \
  && wget https://github.com/Kitware/CMake/releases/download/v3.21.1/cmake-3.21.1.tar.gz \
  && tar xvf cmake-3.21.1.tar.gz \
  && cd cmake-3.21.1 \
  && ./bootstrap \
  && make \
  && make install


ENV ROSE_HOME=/usr/rose
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

RUN groupadd -g 8088 builder && \
   useradd -m -d /home/builder -s /bin/bash -u 8088 -g builder -G sudo builder

RUN echo "builder:builder" | chpasswd

RUN mkdir /share && chmod a+rwx /share && chmod +t /share


USER builder
ENV USER=builder
COPY --chown=builder rose-utils/ /share/rose-utils
COPY --chown=builder ice-locus-dev/ /share/ice-locus-dev
COPY --chown=builder pocc-1.1/ /share/pocc-1.1
RUN mkdir /share/uiuc-compiler-opts
COPY --chown=builder uiuc-compiler-opts/ /share/uiuc-compiler-opts/src-git

WORKDIR /share/rose-utils
RUN ./build.sh

USER root
WORKDIR /share/ice-locus-dev
RUN python3 setup.py install

USER builder
# Setup for subversion proxy
# COPY foo /home/builder/.subversion/servers

RUN mkdir /share/pips
COPY --chown=builder gen_svn_servers.sh /share/pips
WORKDIR /share/pips
RUN alias g77=gfortran
RUN wget https://scm.cri.ensmp.fr/svn/nlpmake/trunk/makes/setup_pips.sh \
   && chmod +x setup_pips.sh \
   && ./gen_svn_servers.sh \
   && ./setup_pips.sh --dynamic --light --pyconf=python3-config


# Setting up following https://bitbucket.org/thiagotei/uiuc-compiler-opts/wiki/Home

USER builder
ENV CC=gcc-4.9
ENV CXX=g++-4.9
WORKDIR /share/pocc-1.1
RUN ./install.sh && cd analyzers/candl && patch -p1 -i ../../pocc-1.1-candl-0.6.2.patch && make install

# Build UIUC Compiler Optimizations
# Ensure using new version of GCC/G++ (should be 9.3.0 for this container)
# Updated: use GCC/G++ (version 8.4.0) to ensure all tools build (incl Locus-Lore)
ENV CC=gcc-8
ENV CXX=g++-8
WORKDIR /share/uiuc-compiler-opts
# Comment out a line in CMakeLists.txt to use system boost
RUN mkdir build && mkdir install && cd build && sed -i '/^set(Boost_NO_SYSTEM_PATHS ON)/ s/^/#/' ../src-git/CMakeLists.txt \
   && sed -i 's|#set(POCC_ROOT "/shared/pocc/pocc-1.1")|set(POCC_ROOT "/share/pocc-1.1")|g' ../src-git/CMakeLists.txt \
   && cmake -DROSE_PATH=/usr/rose -DCMAKE_CXX_FLAGS=-std=c++11 -DCMAKE_INSTALL_PREFIX=/share/uiuc-compiler-opts/install ../src-git \
   && make install
