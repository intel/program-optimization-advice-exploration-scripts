#!/bin/bash

PIN_TAR_BALL=pin-3.27-98718-gbeaa5d51e-gcc-linux.tar.gz
PIN_TOOL_NAME=HuskyFuncTrace
# Build source code extractor
make clean; make

# Build pin-based data extractor
cd ..
wget https://software.intel.com/sites/landingpage/pintool/downloads/${PIN_TAR_BALL}
tar xvf ${PIN_TAR_BALL}
rm ${PIN_TAR_BALL}
ln -s pin-3.27-98718-gbeaa5d51e-gcc-linux pin

export PIN_ROOT=$(readlink -f pin)

pushd ${PIN_ROOT}/source/tools
ln -s ../../../codelet-extractor/src/pin-trace-memory-accesses ${PIN_TOOL_NAME}
cd ..
# Add our pin tool to build list
sed -i "s/ALL_TEST_DIRS := /ALL_TEST_DIRS := "${PIN_TOOL_NAME}"/g" makefile
cd ${PIN_TOOL_NAME}
mkdir obj-intel64
make obj-intel64/${PIN_TOOL_NAME}.so
echo "Done building pin tool : ${PIN_TOOL_NAME}"
popd
