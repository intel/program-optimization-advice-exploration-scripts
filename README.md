Loop Extractor
==============

Installation
-------------------------
1. Clone repo
2. Build local container image
3. Install Intel Advisor
4. Install compilers (Intel, etc)
5. Run setup.sh script
    5.1 Build pin tool
    5.2 Build loop extractor


5. Install pintool from the repository `https://gitlab.com/sepy97/trace-memory-accesses/-/tree/dw` (look at the README of this pintool repository for installation hints)
    5.1. Use `dw` branch (tool called HuskyTool) for a basic version of memory tracing tool
    5.2 Use `main` branch (tool called HuskyFuncTrace) for a modern version of memory tracing tool (that uses callgraph data and trace memory accesses in function calls too)

Building Tools
--------------

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

