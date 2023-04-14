Loop Extractor
==============

Installation
-------------------------
1. Clone repo
2. Install Intel Advisor
3. Install compilers (Intel, etc)
4. Run setup.sh script
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

Below include some sample steps to try the loop extractor.  Assuming the working directory is `/path/to/working` and the repo is checked out at `/path/to/working/codelet-extractor`.
```

### Testing using SPEC2017

1. Create SPEC2017 directory at `/path/to/working/SPEC2017`
2. Put the benchmark under `/path/to/working/SPEC2017/benchmark` so that `/path/to/working/SPEC2017/benchmark/LICENSE.txt` is the SPEC license file
3. Checkout LLVM CMake scripts for SPEC (i.e. perform the following command under `/path/to/working/SPEC2017`)
```
git clone git@github.com:llvm/llvm-test-suite
```
4. Run the Loop extractor
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
2. Ensure `spec_run = False` in extractCodelet.py
3. Run the Loop extractor
* Adapt the prefix variable in script to `/path/to/working`.
* Run the python script under `/path/to/working/codelet-extractor` directory.
```
python extractCodelet.py

```