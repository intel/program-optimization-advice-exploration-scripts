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
   time cpufrequtils numactl curl \
# needed software for CERE
   llvm-7 llvm-7-dev clang-7 flang-7 llvm-7-tools \
   autoconf automake libtool \
   ruby ruby-dev libgoogle-perftools-dev google-perftools \
   dc opt libgmp3-dev \
   libomp-7-dev \
   python3-matplotlib \
#   python3-jinja2 \
   python3-numpy python3-pulp python3-pydot \
   libgraphviz-dev python3-pygraphviz python3-pydotplus python3-networkx && \
   python3 -m pip install --no-cache-dir "certifi>=2023.7.22" "joblib>=1.2.0" "requests>=2.31.0" \
        "urllib3>=2.0.7" "scipy>=1.10.0" "pandas>=1.4.3" && \
   # install skleran via apt-get after pip installs for SDP version needs
   apt-get install --no-install-recommends -y python3-sklearn

# Ronn is needed even if we don't built CERE document
RUN gem install nokogiri -v 1.15.5 && \
	gem install ronn-ng -v 0.9.1 


SHELL ["/bin/bash", "-o", "pipefail", "-c"]
#RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash -

RUN apt-get install --no-install-recommends -y \
# most recent version of compilers
   make gcc g++ gfortran && \
# Need to install gcc-4.9 
# See https://askubuntu.com/questions/1235819/ubuntu-20-04-gcc-version-lower-than-gcc-7
   echo "deb https://mirrors.dotsrc.org/ubuntu/ xenial main" >> /etc/apt/sources.list && echo "deb https://mirrors.dotsrc.org/ubuntu/ xenial universe" >> /etc/apt/sources.list && \
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
   ninja-build \
# web servers
   nodejs libapache2-mod-wsgi-py3 \
   apache2 mariadb-server libmysqlclient-dev 
#   && apt-get clean \
#   && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir sympy \
   && python3 -m pip install --no-cache-dir csvkit \
  && python3 -m pip install --no-cache-dir openpyxl \
  && python3 -m pip install --no-cache-dir et_xmlfile \
  && python3 -m pip install --no-cache-dir Cheetah3 \
  && python3 -m pip install --no-cache-dir parse \
  && python3 -m pip install --no-cache-dir pytrie \
  && python3 -m pip install --no-cache-dir pandas \
  && python3 -m pip install --no-cache-dir numpy \
  && python3 -m pip install --no-cache-dir Jinja2>=3.1.3 \
  && python3 -m pip install --no-cache-dir py-cpuinfo

# Build cmake
# NOTE: NEED NEW VERSION OF CMAKE to build code (e.g. amg)
# See: https://apt.kitware.com/
#wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - |  tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null
RUN curl -L https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - |  tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null \
  && echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ focal main' |  tee /etc/apt/sources.list.d/kitware.list >/dev/null \
  && apt-get update \
  && apt-get install --no-install-recommends -y cmake=3.29.0-0kitware1ubuntu20.04.1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /root
# replace wget by curl
#RUN wget -q https://github.com/Kitware/CMake/releases/download/v3.21.1/cmake-3.21.1.tar.gz \
#RUN curl -L -O https://github.com/Kitware/CMake/releases/download/v3.21.1/cmake-3.21.1.tar.gz \
#  && tar xvf cmake-3.21.1.tar.gz 
#WORKDIR /root/cmake-3.21.1
#RUN ./bootstrap \
#  && make \
#  && make install

ENV ROSE_HOME=/usr/rose
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

RUN mkdir /share && chmod a+rwx /share && chmod +t /share

# Set LLVM-config default to llvm7 (get ready for CERE installation)
RUN update-alternatives --install /usr/bin/llvm-config llvm-config /usr/bin/llvm-config-7 200

# Build CERE
COPY cere /share/cere
WORKDIR /share/cere

# Don't generate document which will fail
RUN sed -i 's| doc/||g' Makefile.am

RUN ./autogen.sh && ./configure && make && make install

# Update library path to include CERE library which is under /usr/local/lib
RUN ldconfig

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
# replace wget by curl
#RUN wget -q https://scm.cri.ensmp.fr/svn/nlpmake/trunk/makes/setup_pips.sh \
RUN curl -L -O https://scm.cri.ensmp.fr/svn/nlpmake/trunk/makes/setup_pips.sh \
   && chmod +x setup_pips.sh \
   && ./gen_svn_servers.sh \
   && ./setup_pips.sh --dynamic --light --pyconf=python3-config

# Setting up following https://bitbucket.org/thiagotei/uiuc-compiler-opts/wiki/Home
COPY pocc-1.1/ /share/pocc-1.1
WORKDIR /share/pocc-1.1
ENV CC=gcc-4.9
ENV CXX=g++-4.9
RUN ./install.sh 
WORKDIR /share/pocc-1.1/analyzers/candl
RUN patch -p1 -i ../../pocc-1.1-candl-0.6.2.patch && make install

# Build UIUC Compiler Optimizations
# Ensure using new version of GCC/G++ (should be 9.3.0 for this container)
# Updated: use GCC/G++ (version 8.4.0) to ensure all tools build (incl Locus-Lore)
RUN mkdir /share/uiuc-compiler-opts
COPY uiuc-compiler-opts/ /share/uiuc-compiler-opts/src-git
ENV CC=gcc-8
ENV CXX=g++-8
WORKDIR /share/uiuc-compiler-opts
# Comment out a line in CMakeLists.txt to use system boost
RUN mkdir build && mkdir install 
WORKDIR /share/uiuc-compiler-opts/build 
RUN sed -i '/^set(Boost_NO_SYSTEM_PATHS ON)/ s/^/#/' ../src-git/CMakeLists.txt \
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
# CERE install its Python packages to site-packages directory
ENV PYTHONPATH=/usr/local/lib/python3.8/site-packages
WORKDIR /app/runner

CMD ["/bin/bash"]
