# QaaS CLI
Using QaaS CLI (backplane scripts)
```
git clone https://gitlab.com/davidwong/qaas.git
cd qaas/qaas-backplane/src
./qaas.py --help
usage: qaas.py [-h] -ap <input-file> [--logic {demo,strategizer}] [-nc] [-D | -q]

This is QaaS backend service.

options:
  -h, --help            show this help message and exit
  -ap <input-file>, --app-params <input-file>
                        name the input file (including suffix)
  --logic {demo,strategizer}
                        Select the QaaS run strategy
  -nc, --no-container   Disable container mode
  -D, --debug           debug mode
  -q, --quiet           quiet mode
```

# Configuration

## Install system dependencies
```
sudo apt-get install -y git git-lfs python3-pip numactl cmake ninja-build
```

## Install python dependencies
```
pip3 install pytrie numpy py-cpuinfo
```

## Install compilers for Intel X86 platforms
Current version of QaaS relies exclusively on Intel's oneapi software (compiler + MPI) and GNU compilers. 
Consequently, these must be installed prior to any use of QaaS on all compute nodes.

---
**NOTE:**

Compilers and parallel runtime configuration is necessary on each machine if the management (where QaaS backplane scripts are installed node and compute nodes are the same.
---

Compilers configuration can be acheived by running the experimental `setup_compilers.sh` script.
```
cd /<path where qaas git is cloned>/scripts
sudo ./setup_compilers.sh
```

If the compilers configuration step works correctly you should see the following:
```
tree /opt/compilers/
/opt/compilers/
├── gcc
│   └── gcc-11.3
│       └── Linux
│           ├── install
│           │   ├── g++ -> /usr/bin/g++-11
│           │   ├── gcc -> /usr/bin/gcc-11
│           │   └── gfortran -> /usr/bin/gfortran-11
│           └── intel64
│               └── load.sh
└── intel
    └── 2023
        └── Linux
            └── intel64
                └── load.sh
```

## Update qaas.conf configuration
QaaS relies on a global configuration file `qaas/qaas-backplane/config/qaas.conf` to control QaaS runs.
Users must modify the following parameters:
- `QAAS_ROOT`: path to where QaaS runs are stored.
- `QAAS_SCRIPT_ROOT`: path to QaaS scripts root file system so that `$QAAS_SCRIPT_ROOT/qaas-service` is accessible on compute nodes.
- `QAAS_COMPILERS_ROOT_DIRECTORT` : path to QaaS scripts to source compilers and Intel runtime.
- `QAAS_USER` : target user name on the compute node for ssh access (password-less must configured
- `QAAS_MACHINE`: machine name of target node where to perform QaaS runs (localhost by default)

# Running QaaS

In order to perform QaaS runs on a target application, a json specfication must be available. 
`<path to qaas root>/demo/json_inputs/` contains multiple examples of apps to runs.

```
cd qaas
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer --no-container -D
```

Will run the QaaS strategizer (only unicore logic for now) using the debug mode but with container mode disabled.
