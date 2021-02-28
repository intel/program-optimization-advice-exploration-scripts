Loop Extractor
==============

Installation (Ubuntu 16+)
-------------------------
1. Clone repo
2. Build ROSE(version: 0.9.8.8 or above)
3. Build Boost(version: 1.61.0)
4. Add path to Rose(Build) and Boost header and library files in the Makefile.

Installation (Ubuntu 18+)
-------------------------
1. Clone repo
2. Install ROSE (Boost included) using `apt`.
3. Add path to Rose header and library files in the Makefile.

Building Tools
--------------

Recommended ROSE building method: GNU autotools.

ROSE [Installation Guide](https://github.com/rose-compiler/rose/)

Installing ROSE using `apt`:
```
apt-get install -y software-properties-common
add-apt-repository -y ppa:rosecompiler/rose-stable # Replace rose-development with rose-stable for release version
apt-get install -y rose
apt-get install -y rose-tools # Optional: Installs ROSE tools in addition to ROSE Core
```

Building the Loop Extractor
-----------------------

GCC/G++ version-4.9, 5.4 or above

Use `make` to generate the executable.


Using the Loop Extractor
------------------------

Run the executable without any arguments to see all available options.

Example:
```
# Extract loop nests (with OpenMP pragmas) into separate files
./bin/LoopExtractor tests/testing.c
# Compile C code
gcc LoopExtractor_data/testing_base_tests.c \
    LoopExtractor_data/testing_main_line17_tests.c \
    LoopExtractor_data/testing_main_line27_tests.c -lm -fopenmp
```

This should create a folder in the current directory called `LoopExtractor_data`.

Inside there should be a `base` file (i.e. similar to original file but without loop nests) 
and multiple `loop nest` files (i.e. files containing extracted loop nests that are called from the `base` file).

All required header files are copied to the data folder and pre-processing of the source files is done while loop extraction.

Multiple source files can be provided in the command line to the Loop Extractor. Just like you would do for compiling a C/C++ project.

To tell the Loop Extractor to skip extracting a loop nest, use `#pragma LE skiploop` over the loop nest in the source file.
