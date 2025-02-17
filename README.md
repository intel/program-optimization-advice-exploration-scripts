# QaaS Scripts
Scripts for Program Optimization Advice Exploration infrastructure

## Installation
1. Clone this repository
2. QaaS container-less installation (prefered mode)
   - Provides QaaS Command-Line Interface (CLI) running mode
   - Follow [QaaS CLI run mode](doc/HOWTO_BACKPLANE.md) for instructions
3. QaaS container installation (experimental)
   - Provides the following components
     - QaaS Web Front (GUI+DB)
     - Extractor Scripts
   - To install, run `setup.sh` script. The script will automatically do the following things:
     1. Build local container image
     2. Run setup.sh scripts under different components of QaaS scripts.
  
## Run QaaS Scripts
- Container-less run mode
  - `cd qaas-backplane/src`
  - `./qaas.py <run options>`
  - Follow [QaaS CLI run mode](doc/HOWTO_BACKPLANE.md) to get more details
- Container run mode
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

## Script development status
Below table capture current script developement status for different environments and different components.  In the table there are diffferent status level:
* Working : Our implementation has been working for various use cases.
* Under development : Our implementation work is in progress so not likely to work but we are working on that.
* To support : Little or no implementation has been done.

| Environment        | Backplane         | Web and database | App Mutator (Locus) | Loop Extractor |
| ------------------ | ----------------- | ---------------- | ------------------- | -------------- |
|   Container-less   | Working           | To support       | To support          | To support     |
| Container (Docker) | Under development | Working          | Under development   | Working        |
| Container (Podman) | Under development | To support       | To support          | To support     |
