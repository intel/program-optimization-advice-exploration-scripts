Loop Extractor
==============

Installation
-------------------------
1. Clone repo
2. Install Intel Advisor
3. Install compilers (Intel, etc)
4. Run setup.sh script
    1. Build pin tool
    2. Build loop extractor
    3. Build Local container image


5. Install pintool from the repository `https://gitlab.com/sepy97/trace-memory-accesses/-/tree/dw` (look at the README of this pintool repository for installation hints)
    5.1. Use `dw` branch (tool called HuskyTool) for a basic version of memory tracing tool
    5.2 Use `main` branch (tool called HuskyFuncTrace) for a modern version of memory tracing tool (that uses callgraph data and trace memory accesses in function calls too)

Building Tools
--------------

Change python script `extractCodelet.py` by providing paths to the benchmark and installed pintool


Using the Loop Extractor
------------------------

Run the python script:
```
python extractCodelet.py
```