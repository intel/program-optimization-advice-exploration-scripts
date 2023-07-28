ARG BASE_IMAGE=ubuntu
ARG BASE_IMAGE_TAG=20.04

FROM ${BASE_IMAGE}:${BASE_IMAGE_TAG}

LABEL maintainer "David Wong / Abdelhafid Mazouz first.last@intel.com>"
LABEL description="Base Image for running QaaS containers"

# Setup container environment work
RUN apt-get update && \
   DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
# processes mngt
   procps psmisc \
# network mngt
   iputils-ping iproute2 wget \
# OS utilities
   pkg-config software-properties-common \
# more basic utilities
   vim less \
# more dev utilities
   git git-lfs \
   python3-pip \
# perf. tools
   time cpufrequtils numactl

RUN apt-get install --no-install-recommends -y \
# most recent version of compilers
   make gcc g++ gfortran && \
# Need to install gcc-4.9 
# See https://askubuntu.com/questions/1235819/ubuntu-20-04-gcc-version-lower-than-gcc-7
   echo "deb http://dk.archive.ubuntu.com/ubuntu/ xenial main" >> /etc/apt/sources.list && echo "deb http://dk.archive.ubuntu.com/ubuntu/ xenial universe" >> /etc/apt/sources.list && \
   add-apt-repository ppa:rosecompiler/rose-development && \
   apt-get update && apt-get install --no-install-recommends -y \
# Following steps from ROSE website: https://github.com/rose-compiler/rose/wiki/Install-Using-apt-get
   rose \
# Optional: Installs ROSE tools in addition to ROSE Core
   rose-tools \
# More utilities specified at https://gitlab.com/Wingpad/rose-utils
   default-jdk \
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
   binutils-dev libiberty-dev \
# For fast app build
   ninja-build

RUN python3 -m pip install sympy \
  && python3 -m pip install csvkit \
  && python3 -m pip install openpyxl \
  && python3 -m pip install et_xmlfile \
  && python3 -m pip install Cheetah3 \
  && python3 -m pip install parse \
  && python3 -m pip install pytrie \
  && python3 -m pip install pandas \
  && python3 -m pip install py-cpuinfo

# Build cmake
# NOTE: WHY WE NEED A SPECFIC VERSION instead of apt install cmake
RUN cd /root \
  && wget https://github.com/Kitware/CMake/releases/download/v3.21.1/cmake-3.21.1.tar.gz \
  && tar xvf cmake-3.21.1.tar.gz \
  && cd cmake-3.21.1 \
  && ./bootstrap \
  && make \
  && make install

ENV ROSE_HOME=/usr/rose
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

RUN mkdir /share && chmod a+rwx /share && chmod +t /share

# Setup ROSE utils
COPY rose-utils-for-qaas/ /share/rose-utils
WORKDIR /share/rose-utils
RUN ./build.sh

#Setup LOCUS
COPY ice-locus-dev/ /share/ice-locus-dev
WORKDIR /share/ice-locus-dev
RUN python3 setup.py install

#Setup FDO-LIB
COPY fdo-lib/ /share/fdo-lib
WORKDIR /share/fdo-lib
RUN python3 setup.py install

# Setup pips
USER root
ENV USER=root
RUN mkdir /share/pips
COPY gen_svn_servers.sh /share/pips
WORKDIR /share/pips
RUN alias g77=gfortran
RUN wget https://scm.cri.ensmp.fr/svn/nlpmake/trunk/makes/setup_pips.sh \
   && chmod +x setup_pips.sh \
   && ./gen_svn_servers.sh \
   && ./setup_pips.sh --dynamic --light --pyconf=python3-config

# Setting up following https://bitbucket.org/thiagotei/uiuc-compiler-opts/wiki/Home
COPY pocc-1.1/ /share/pocc-1.1
WORKDIR /share/pocc-1.1
ENV CC=gcc-4.9
ENV CXX=g++-4.9
RUN ./install.sh && cd analyzers/candl && patch -p1 -i ../../pocc-1.1-candl-0.6.2.patch && make install

# Build UIUC Compiler Optimizations
# Ensure using new version of GCC/G++ (should be 9.3.0 for this container)
# Updated: use GCC/G++ (version 8.4.0) to ensure all tools build (incl Locus-Lore)
RUN mkdir /share/uiuc-compiler-opts
COPY uiuc-compiler-opts/ /share/uiuc-compiler-opts/src-git
ENV CC=gcc-8
ENV CXX=g++-8
WORKDIR /share/uiuc-compiler-opts
# Comment out a line in CMakeLists.txt to use system boost
RUN mkdir build && mkdir install && cd build && sed -i '/^set(Boost_NO_SYSTEM_PATHS ON)/ s/^/#/' ../src-git/CMakeLists.txt \
   && sed -i 's|#set(POCC_ROOT "/shared/pocc/pocc-1.1")|set(POCC_ROOT "/share/pocc-1.1")|g' ../src-git/CMakeLists.txt \
   && cmake -DROSE_PATH=/usr/rose -DCMAKE_CXX_FLAGS=-std=c++11 -DCMAKE_INSTALL_PREFIX=/share/uiuc-compiler-opts/install ../src-git \
   && make install

# Setup QaaS scripts for build & run
RUN mkdir /qaas
COPY app_builder.py /qaas
COPY app_runner.py /qaas
RUN mkdir -p /app/builder /app/runner
RUN groupadd -g 8888 qaas && \
    useradd -m -d /home/qaas -s /bin/bash -u 8888 -g qaas qaas && \
    chown qaas:qaas /app/builder && \
    chown qaas:qaas /app/runner

# Setup user run directories
USER qaas
ENV USER=qaas
ENV ICE_CMPOPTS_PATH=/share/uiuc-compiler-opts/install
WORKDIR /app/runner

CMD ["/bin/bash"]
