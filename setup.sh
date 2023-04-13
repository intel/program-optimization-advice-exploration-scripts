#!/bin/bash

# Build source code extractor
make clean; make

# Build pin-based data extractor
wget https://software.intel.com/sites/landingpage/pintool/downloads/pin-3.27-98718-gbeaa5d51e-gcc-linux.tar.gz
cd ..
tar xvf ../pin-3.27-98718-gbeaa5d51e-gcc-linux.tar.gz
ln -s pin-3.27-98718-gbeaa5d51e-gcc-linux pin