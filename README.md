Loop Extractor
==============

Installation
-------------------------
1. Clone repo
2. Install Intel Advisor
   - The extractor right now hardcoded the Advisor so that the env loading script is at `/host/opt/intel/oneapi/advisor/2023.0.0/advisor-vars.sh`
3. Install compilers (Intel, etc)
4. Run setup.sh script.  The script will automatically do the following things:
    1. Build Local container image
    2. Download pin
    3. Build pin tool
    4. Build loop extractor

Using the Loop Extractor
------------------------

### General command
Run the python script:
```
python extractCodelet.py
```
Below include some sample steps to try the loop extractor.  Assuming the working directory is _path_to_working_ and the repo is checked out at _path_to_working_/`codelet-extractor`.


### Testing using SPEC2017

1. Create SPEC2017 directory at `/path/to/working/SPEC2017`
2. Put the benchmark under `/path/to/working/SPEC2017/benchmark` so that `/path/to/working/SPEC2017/benchmark/LICENSE.txt` is the SPEC license file
3. Checkout LLVM CMake scripts for SPEC (i.e. perform the following command under `/path/to/working/SPEC2017`)
   ```
   git clone git@github.com:llvm/llvm-test-suite
   ```
4. Go to the script directory `/path/to/working/codelet-extractor`.
5. Ensure `spec_run = True` in `extractCodelet.py`   
6. Start container `./container/run-container.sh`.
7. Make sure you source needed compiler scripts to set up the `PATH`, `LD_LIBRARY_PATH` and other variables.
8. Run the Loop extractor
   * Adapt the prefix variable in script to `/path/to/working`.
   * Run the python script under `/path/to/working/codelet-extractor` directory.
   ```
   python extractCodelet.py
   ```

### Testing using CloverLeaf application

1. Checkout updated CloverLeaf app 
   ```
   git clone git@gitlab.com:davidwong/CloverLeaf.git
   ```
2. Go to the script directory `/path/to/working/codelet-extractor`.
3. Ensure `spec_run = False` in `extractCodelet.py`
4. Start container `./container/run-container.sh`.
5. Make sure you source needed compiler scripts to set up the `PATH`, `LD_LIBRARY_PATH` and other variables.
6. Run the Loop extractor
   * Adapt the prefix variable in script to `/path/to/working`.
   * Run the python script under `/path/to/working/codelet-extractor` directory.
   ```
   python extractCodelet.py
   ```