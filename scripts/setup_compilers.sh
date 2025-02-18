#!/bin/bash

# Install Intel compilers
if [[ ! -f "/etc/apt/sources.list.d/oneAPI.list" ]]; then
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /etc/apt/trusted.gpg.d/oneapi-archive-keyring.gpg > /dev/null
echo "deb https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list
apt-get update
fi

if [[ ! -d "/opt/intel/oneapi/compiler" ]]; then
	apt-get install -y intel-oneapi-compiler-dpcpp-cpp-and-cpp-classic intel-oneapi-compiler-fortran
fi
if [[ ! -d "/opt/intel/oneapi/mkl" ]]; then
	apt-get install -y intel-oneapi-mkl intel-oneapi-mkl-devel
fi
if [[ ! -d "/opt/intel/oneapi/mpi" ]]; then
	apt-get install -y intel-oneapi-mpi intel-oneapi-mpi-devel
fi

PREFIX=/opt/compilers2
mkdir -p $PREFIX 
cd $PREFIX
COMPILER_PATH=$(ls -1art /opt/intel/oneapi/compiler/*/env/vars.sh | sed 's:.*latest.*::;/^$/d' | tail -n 1)
VERSION=$(echo ${COMPILER_PATH} | cut -d'/' -f6)
YEAR=$(echo $VERSION | cut -d'.' -f1)
mkdir -p intel/${YEAR}/env/
echo "source /opt/intel/oneapi/compiler/${VERSION}/env/vars.sh" >  intel/${YEAR}/env/load.sh
echo "source /opt/intel/oneapi/mkl/${VERSION}/env/vars.sh"      >> intel/${YEAR}/env/load.sh
MPIVER=$(ls -1 /opt/intel/oneapi/mpi/*/env/vars.sh | sed 's:.*latest.*::;/^$/d' | tail -n 1 | cut -d'/' -f6)
echo "source /opt/intel/oneapi/mpi/${MPIVER}/env/vars.sh"       >> intel/${YEAR}/env/load.sh
ln -frs intel/${YEAR} intel/latest

# Install gcc
cd $PREFIX
gccversion="11.4"
mkdir -p gcc/gcc-${gccversion}/env/
# Simulate install with system provided gcc
mkdir -p gcc/gcc-${gccversion}/install/
ln -s /usr/bin/gcc-11      gcc/gcc-${gccversion}/install/gcc
ln -s /usr/bin/g++-11      gcc/gcc-${gccversion}/install/g++
ln -s /usr/bin/gfortran-11 gcc/gcc-${gccversion}/install/gfortran
echo "export PATH=${PREFIX}/gcc/gcc-${gccversion}/install:\$PATH" >  gcc/gcc-${gccversion}/env/load.sh
echo "source /opt/intel/oneapi/mkl/${VERSION}/env/vars.sh"              >> gcc/gcc-${gccversion}/env/load.sh
echo "source /opt/intel/oneapi/mpi/${MPIVER}/env/vars.sh"               >> gcc/gcc-${gccversion}/env/load.sh
#echo "source ${PREFIX}/gcc/gcc-${gccversion}/env/load.sh"     >> intel/${YEAR}/env/load.sh
ln -frs gcc/gcc-${gccversion} gcc/latest
