# QaaS Scripts
Scripts for Program Optimization Advice Exploration infrastructure

## Installation
1. Clone this repository
2. Run setup.sh script.  The script will automatically do the following things:
   1. Build local container image
   2. Run setup.sh scripts under different components of QaaS scripts.
  
## Run QaaS Scripts
- Start container
  - `cd container`
  - `./run-container.sh`
- Run Demo script
  - `cd ../scripts`
  - `python demo.py`

## Run QaaS Web Front
Follow [Run QaaS Web Front section](qaas-web/README.md#run-qaas-web-front) of QaaS Web document.

## Run Extractor Scripts
Follow [Using the Loop Extractor section](qaas-extractor/README.md#using-the-loop-extractor) of Loop Extractor document.

## Container maintance (under `container` directory)
Follow [Container maintance section](container/README.md#container-maintance) of container document.
