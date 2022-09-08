Loop Extractor
==============

Installation (Ubuntu 18+)
-------------------------
1. Clone repo
2. Install ROSE (Boost included) using `apt`.
3. Add path to Rose header and library files in the Makefile.
4. (temporary workaround for Ubuntu 20+) Install gcc-7 (and g++-7) in addition to gcc-9 (g++-9), go to `/usr/include/c++` and make a symlink: `sudo mv 9 bckp_9 && sudo ln -s 7 9`
5. Install pintool from the repository `https://gitlab.com/sepy97/trace-memory-accesses/-/tree/dw` (look at the README of this pintool repository for installation hints)
    5.1. Use `dw` branch (tool called HuskyTool) for a basic version of memory tracing tool
    5.2 Use `main` branch (tool called HuskyFuncTrace) for a modern version of memory tracing tool (that uses callgraph data and trace memory accesses in function calls too)
6. Make sure that OneView is installed from the repository `https://gitlab.com/davidwong/cape-experiment-scripts/-/tree/master` ; if not, either install OneView and write its path to the `extractCodelet.py` or comment out `runOneView` function call in `extractCodelet.py` script

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

Change python script `extractCodelet.py` by providing paths to the benchmark and installed pintool

Building the Loop Extractor
-----------------------

GCC/G++ version-7 or above

Use `make` to generate the executable.


Using the Loop Extractor
------------------------

Run the python script:
```
python extractCodelet.py
```

Dockerfile
------------------------

There is a Dockerfile in the repository; ideally, all the setup should exists inside of the container. However, it's not finished due to issues with running a building commmand (`RUN make`).

