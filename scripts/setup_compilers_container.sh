#!/bin/bash

# Install Intel compilers
if [[ ! -f "/etc/apt/sources.list.d/oneAPI.list" ]]; then
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | tee /etc/apt/trusted.gpg.d/oneapi-archive-keyring.gpg > /dev/null
echo "deb https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list
apt-get update
fi

# Maps from compiler versions to their corresponding runtime to be source'd in load.sh
declare -A compiler_verion_map=([2023]="2023.2.3-20" [2024]="2024.0.2-49895")
declare -A compiler_folder_map=([2023]="2023.2.3" [2024]="2024.0")
declare -A mkl_verion_map=([2023]="2023.2.0-49495" [2024]="2024.0.0-49656")
declare -A mkl_folder_map=([2023]="2023.2.0" [2024]="2024.0")
declare -A mpi_verion_map=([2023]="2021.11.0-49493" [2024]="2021.11.0-49493")
declare -A mpi_folder_map=([2023]="2021.11" [2024]="2021.11")

PREFIX=/opt/compilers
for version in 2023 2024; do
  compiler_version=${compiler_verion_map[$version]}
  mkl_version=${mkl_verion_map[$version]}
  mpi_version=${mpi_verion_map[$version]}
	if (( version > 2023)); then
		c_cxx_compiler_package=intel-oneapi-compiler-dpcpp-cpp
	else
		c_cxx_compiler_package=intel-oneapi-compiler-dpcpp-cpp-and-cpp-classic
	fi
  echo For compiler $version, install compiler: ${compiler_package}-${compiler_version}, mkl: ${mkl_version}, mpi: ${mpi_version}
	apt-get install -y ${c_cxx_compiler_package}=${compiler_version} intel-oneapi-compiler-fortran=${compiler_version}
	apt-get install -y intel-oneapi-mkl=${mkl_version} intel-oneapi-mkl-devel=${mkl_version}
	apt-get install -y intel-oneapi-mpi=${mpi_version} intel-oneapi-mpi-devel=${mpi_version}
	mkdir -p ${PREFIX}/intel/${version}/Linux/intel64/
  compiler_folder=${compiler_folder_map[$version]}
  mkl_folder=${mkl_folder_map[$version]}
  mpi_folder=${mpi_folder_map[$version]}
	echo "source /opt/intel/oneapi/compiler/${compiler_folder}/env/vars.sh" >  ${PREFIX}/intel/${version}/Linux/intel64/load.sh
	echo "source /opt/intel/oneapi/mkl/${mkl_folder}/env/vars.sh"      >> ${PREFIX}/intel/${version}/Linux/intel64/load.sh
	echo "source /opt/intel/oneapi/mpi/${mpi_folder}/env/vars.sh"       >> ${PREFIX}/intel/${version}/Linux/intel64/load.sh
done
ln -frs ${PREFIX}/intel/${version} ${PREFIX}/intel/latest

# Install gcc
# Install gcc-11.4
# See: https://www.reddit.com/r/Ubuntu/comments/ptixle/is_there_a_ppa_that_always_has_the_latest_gcc/
add-apt-repository ppa:ubuntu-toolchain-r/test
apt-get -y install gcc-11 g++11 gfortran-11

cd $PREFIX
gccversion="11.4"
mkdir -p gcc/gcc-${gccversion}/Linux/intel64/
# Simulate install with system provided gcc
mkdir -p gcc/gcc-${gccversion}/Linux/install/
ln -s /usr/bin/gcc-11      gcc/gcc-${gccversion}/Linux/install/gcc
ln -s /usr/bin/g++-11      gcc/gcc-${gccversion}/Linux/install/g++
ln -s /usr/bin/gfortran-11 gcc/gcc-${gccversion}/Linux/install/gfortran
echo "export PATH=${PREFIX}/gcc/gcc-${gccversion}/Linux/install:\$PATH" >  gcc/gcc-${gccversion}/Linux/intel64/load.sh
# Use the "latest" MKL and MPI folders
echo "source /opt/intel/oneapi/mkl/${mkl_folder}/env/vars.sh"              >> gcc/gcc-${gccversion}/Linux/intel64/load.sh
echo "source /opt/intel/oneapi/mpi/${mpi_folder}/env/vars.sh"               >> gcc/gcc-${gccversion}/Linux/intel64/load.sh
#echo "source ${PREFIX}/gcc/gcc-${gccversion}/Linux/intel64/load.sh"     >> intel/${YEAR}/Linux/intel64/load.sh
ln -frs gcc/gcc-${gccversion} gcc/latest
