#!/bin/bash

PIN_TAR_BALL=pin-3.27-98718-gbeaa5d51e-gcc-linux.tar.gz
PIN_TOOL_NAME=HuskyFuncTrace

if [[ ${USER} != "qaas" ]]; then
  echo "Outside container setting up local image and then resume inside container"
  # Build local image
  pushd container
  ./build-local-image.sh

  # Download pin while outside container
  cd ../..
  wget https://software.intel.com/sites/landingpage/pintool/downloads/${PIN_TAR_BALL}
  tar xvf ${PIN_TAR_BALL}
  rm ${PIN_TAR_BALL}
  ln -s $(basename ${PIN_TAR_BALl} .tar.gz) pin

  # Run the script again inside to set up the rest
  popd
  ./container/run-container.sh ./setup.sh
  # Done, quit and not the execute code below.
  exit
fi

echo "Now setting up rest inside container"
# Currently under the directory of setup.sh

# Build source code extractor
make clean; make

# Build pin-based data extractor
cd ..
export PIN_ROOT=$(readlink -f pin)

pushd ${PIN_ROOT}/source/tools
ln -s ../../../codelet-extractor/src/pin-trace-memory-accesses ${PIN_TOOL_NAME}
# Add our pin tool to build list
sed -i "s/ALL_TEST_DIRS := /ALL_TEST_DIRS := "${PIN_TOOL_NAME}"/g" makefile
cd ${PIN_TOOL_NAME}
mkdir obj-intel64
make obj-intel64/${PIN_TOOL_NAME}.so
echo "Done building pin tool : ${PIN_TOOL_NAME}"
popd

echo "Finished rest of setup inside the container."
echo "To use extractor, please run container/run-container.sh and try the extractCodelet.py script."