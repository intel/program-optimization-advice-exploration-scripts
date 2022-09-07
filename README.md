Loop Extractor
==============

Installation (Ubuntu 18+)
-------------------------
1. Clone repo
2. Install ROSE (Boost included) using `apt`.
3. Add path to Rose header and library files in the Makefile.
4. (temporary workaround for Ubuntu 20+) Install gcc-7 (and g++-7) in addition to gcc-9 (g++-9), go to `/usr/include/c++` and make a symlink: `sudo mv 9 bckp_9 && sudo ln -s 7 9`
5. Install pintool from the repository `https://gitlab.com/sepy97/trace-memory-accesses/-/tree/dw`

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



