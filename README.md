Loop Extractor

Installation (Ubuntu 16+):
1. Clone repo
2. Build ROSE(version: 0.9.8.8 or above)
3. Build Boost(version: 1.61.0)
4. Add path to Rose(Build) and Boost header and library files in the Makefile.

Installation (Ubuntu 18+):
1. Clone repo
2. Install ROSE (Boost included) using apt.
3. Add path to Rose header and library files in the Makefile.

Building Tools:
GCC/G++ version-4.9 and 5.4

Recommended ROSE building method: GNU autotools.

Other [Installation Guide](https://github.com/rose-compiler/rose/)

If CUDA is not installed, add -Denable-cuda:BOOL=off in ROSE CMake build.

Installing ROSE using `apt`:
```
apt-get install -y software-properties-common
add-apt-repository -y ppa:rosecompiler/rose-stable # Replace rose-development with rose-stable for release version
apt-get install -y rose
apt-get install -y rose-tools # Optional: Installs ROSE tools in addition to ROSE Core
```

Source:
Formatting Style: clang-format -style="{BasedOnStyle: llvm, AlignConsecutiveAssignments: true}" -i <file>
