#!/bin/bash

# Install Intel compilers

if [[ ! -f "/etc/apt/sources.list.d/oneAPI.list" ]]; then
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /etc/apt/trusted.gpg.d/oneapi-archive-keyring.gpg > /dev/null
echo "deb https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list
fi
apt-get update

apt-get install -y intel-oneapi-compiler-dpcpp-cpp-and-cpp-classic-2022.2.1 intel-oneapi-compiler-fortran-2022.2.1
apt-get install -y intel-oneapi-mkl-2022.2.1 intel-oneapi-mkl-devel-2022.2.1
apt-get install -y intel-oneapi-mpi-2021.7.1 intel-oneapi-mpi-devel-2021.7.1

apt-get install -y intel-oneapi-compiler-dpcpp-cpp-and-cpp-classic intel-oneapi-compiler-fortran
apt-get install -y intel-oneapi-mkl intel-oneapi-mkl-devel
apt-get install -y intel-oneapi-mpi intel-oneapi-mpi-devel

mkdir -p /opt/compilers
cd /opt/compilers
mkdir -p intel/2023/Linux/intel64/
echo "source /opt/intel/oneapi/compiler/2023.1.0/env/vars.sh" >  intel/2023/Linux/intel64/load.sh
echo "source /opt/intel/oneapi/mkl/2023.1.0/env/vars.sh"      >> intel/2023/Linux/intel64/load.sh
echo "source /opt/intel/oneapi/mpi/2021.9.0/env/vars.sh"     >> intel/2023/Linux/intel64/load.sh
mkdir -p intel/2022/Linux/intel64/
echo "source /opt/intel/oneapi/compiler/2022.2.1/env/vars.sh" >  intel/2022/Linux/intel64/load.sh
echo "source /opt/intel/oneapi/mkl/2022.2.1/env/vars.sh"      >> intel/2022/Linux/intel64/load.sh
echo "source /opt/intel/oneapi/mpi/2021.7.1/env/vars.sh"     >> intel/2022/Linux/intel64/load.sh

#Install gcc

ubuntu_version=$(cat /etc/os-release | grep UBUNTU_CODENAME | cut -d'=' -f2)

if [[ ! -f "/etc/apt/sources.list.d/ubuntu-toolchain-r-ubuntu-test-${ubuntu_version}.list" ]]; then
	add-apt-repository -y ppa:ubuntu-toolchain-r/test
fi

apt-get install -y gcc-11 g++-11 gfortran-11
if [[ "${ubuntu_version}" == "jammy" ]]; then
	apt-get install -y gcc-12 g++-12 gfortran-12
fi

cd /opt/compilers
gccversion=$(gcc-11 --version | head -n1 | cut -d' ' -f4 | sed 's:\..$::')
mkdir -p gcc/gcc-${gccversion}/Linux/intel64/
mkdir -p gcc/gcc-${gccversion}/Linux/install/
ln -s $(which gcc-11) gcc/gcc-${gccversion}/Linux/install/gcc
ln -s $(which g++-11) gcc/gcc-${gccversion}/Linux/install/g++
ln -s $(which gfortran-11) gcc/gcc-${gccversion}/Linux/install/gfortran
echo "export PATH=/opt/compilers/gcc/gcc-${gccversion}/Linux/install:$PATH" >  gcc/gcc-${gccversion}/Linux/intel64/load.sh

cd /opt/compilers
if [[ "${ubuntu_version}" == "jammy" ]]; then
gccversion=$(gcc-12 --version | head -n1 | cut -d' ' -f4 | sed 's:\..$::')
mkdir -p gcc/gcc-${gccversion}/Linux/intel64/
mkdir -p gcc/gcc-${gccversion}/Linux/install/
ln -s $(which gcc-12) gcc/gcc-${gccversion}/Linux/install/gcc
ln -s $(which g++-12) gcc/gcc-${gccversion}/Linux/install/g++
ln -s $(which gfortran-12) gcc/gcc-${gccversion}/Linux/install/gfortran
echo "export PATH=/opt/compilers/gcc/gcc-${gccversion}/Linux/install:$PATH" >  gcc/gcc-${gccversion}/Linux/intel64/load.sh
fi
