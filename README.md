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
- For security measures,
  - need to enable HTTPS connection.
  - debug feature is disabled by default.  Developer needs to enable it by updating source code to set debug parameters for various components.
  - to limit the HTTP request body size, can use the maxAllowedContentLength to limit size, or other commands depending on the type of the webservers.
  - User should follow security tips when deploying current webapp to production web servers.
- Also should enable TLS for further safety in data transfer.
- To limit message size, set maxContentLength variable (e.g. to 10000) on React async() call to receive request.

## Run Extractor Scripts
Follow [Using the Loop Extractor section](qaas-extractor/README.md#using-the-loop-extractor) of Loop Extractor document.

## Container maintance (under `container` directory)
Follow [Container maintance section](container/README.md#container-maintance) of container document.
