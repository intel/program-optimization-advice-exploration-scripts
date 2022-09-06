# our local base image
FROM ubuntu:20.04 

LABEL description="Container for use with Codelet Extractor" 

#ENV http_proxy http://proxy-chain.intel.com:911
#ENV https_proxy http://proxy-chain.intel.com:912

# install build dependencies 

RUN apt-get update && apt-get install --no-install-recommends -y make \
 software-properties-common && \
 add-apt-repository ppa:rosecompiler/rose-stable && \
 apt-get update && apt-get install --no-install-recommends -y g++ gcc rsync zip openssh-server \
# Following steps from ROSE website: https://github.com/rose-compiler/rose/wiki/Install-Using-apt-get
   rose \
 # Optional: Installs ROSE tools in addition to ROSE Core
   rose-tools \
# More utilities specified at https://gitlab.com/Wingpad/rose-utils
   default-jdk \
   git git-lfs wget \
# More basic utilities
   vim \
   less \
   sudo \
# Need pkg-config to csvkit
   pkg-config \
# Used in the extraction script
   python3-pip \
# for temporary workaround for Rose
   gcc-7 g++-7 

RUN chmod u+s /usr/bin/cpufreq-set
 
# Temporary workaround for Rose
RUN cd /usr/include/c++ \ 
  && sudo mv 9 bckp_9 \
  && sudo ln -s 7 9

# Used in const.sh
RUN locale-gen en_US.utf8 && update-locale

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
# ?? install pin?
# ?? add pin home directory?

# ????????????????????
RUN groupadd -g 8088 builder && \
   useradd -m -d /home/builder -s /bin/bash -u 8088 -g builder -G sudo builder

RUN echo "builder:builder" | chpasswd

RUN mkdir /share && chmod a+rwx /share && chmod +t /share

# ???????????????????
COPY sep_eng/ /opt/intel/sep_eng
USER builder
ENV USER=builder
COPY --chown=builder rose-utils/ /share/rose-utils
COPY --chown=builder ice-locus-dev/ /share/ice-locus-dev
COPY --chown=builder pocc-1.1/ /share/pocc-1.1
RUN mkdir /share/uiuc-compiler-opts
COPY --chown=builder uiuc-compiler-opts/ /share/uiuc-compiler-opts/src-git

#WORKDIR /share/rose-utils
#RUN ./build.sh
# ?? script to install pintool and codelet-extractor ?

#USER root
#WORKDIR /share/ice-locus-dev
#RUN python3 setup.py install
