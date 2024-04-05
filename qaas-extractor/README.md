Loop Extractor
==============

Installation
-------------------------
1. Follow [topmost installation instruction](../README.md)
   - The topmost setup.sh script will run setup.sh script of Loop Extractor to do the following automatically
     - Build Loop Extractor in backplane container
2. Install Intel Advisor
   - The extractor right now hardcoded the Advisor so that the env loading script is at `/host/opt/intel/oneapi/advisor/2023.0.0/advisor-vars.sh`
3. Install compilers (Intel, etc)

Using the Loop Extractor
------------------------

### General command
Run the python script:
<pre>
python <i>extractor_dir</i>/extractCodelet.py
</pre>
where _extractor_dir_ is the folder containing the `extractCodelet.py` script.  Assuming this extractor is obtained from the program optimization advice exploration script under _topmost_dir_, _extractor_dir_ will be _topmost_dir_/`qaas-extractor`.

Below include some sample steps to try the loop extractor.  Assuming 
- the working directory is _workdir_ 
- the repository is checked out at _workdir_/`applications.services.program-optimization-advice-exploration-scripts`
- so,  _topmost_dir_ is _workdir_/`applications.services.program-optimization-advice-exploration-scripts`.
- and, _extractor_dir_ is  _workdir_/`applications.services.program-optimization-advice-exploration-scripts/qaas-extractor`.


### Testing using SPEC2017

1. Create SPEC2017 directory at _workdir_`/SPEC2017`
2. Put the benchmark under _workdir_/`SPEC2017/benchmark` so that _workdir_/`SPEC2017/benchmark/LICENSE.txt` is the SPEC license file
3. Checkout LLVM CMake scripts for SPEC (i.e. perform the following command under _workdir_/`SPEC2017`)
   ```
   git clone git@github.com:llvm/llvm-test-suite
   ```
4. Go to the script directory _topmost_dir_.
5. Update `qaas-extractor/extractCodelet.py`, set `binary` variable in `main()` to the one of the SPEC benchmarks (e.g.`binary='525.x264_r'`)
6. Start container `./container/run-container.sh`.
7. Make sure you source needed compiler scripts to set up the `PATH`, `LD_LIBRARY_PATH` and other variables.
8. Run the Loop extractor under _workdir_ directory.
<pre>
   cd <i>workdir</i>
   python <i>extractor_dir</i>/extractCodelet.py
</pre>

### Testing using CloverLeaf application

1. Checkout updated CloverLeaf app 
   ```
   git clone git@gitlab.com:davidwong/CloverLeaf.git
   ```
2. Go to the script directory _topmost_dir_.
3. Update `qaas-extractor/extractCodelet.py`, set `binary` variable in `main()` to CloverLeaf app (e.g.`binary='clover_leaf'`)
4. Start container `./container/run-container.sh`.
5. Make sure you source needed compiler scripts to set up the `PATH`, `LD_LIBRARY_PATH` and other variables.
6. Run the Loop extractor under _workdir_ directory.
<pre>
   cd <i>workdir</i>
   python <i>extractor_dir</i>/extractCodelet.py
</pre>
