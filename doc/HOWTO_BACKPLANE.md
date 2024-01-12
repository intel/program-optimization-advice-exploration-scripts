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
  -r, --as-root-in-container
                        Run host users as root in container [permissive rootless mode in podman]. Not allowed for true root users.
  -ncd, --no-compiler-default
                        Disable search for best default compiler
  -ncf, --no-compiler-flags
                        Disable search for best compiler flags
  -p {off,mpi,openmp,hybrid}, --parallel-compiler-runs {off,mpi,openmp,hybrid}
                        Force multiprocessing [MPI, OpenMP or hybrid] for compiler search runs
  -s, --enable-parallel-scale
                        Turn on multicore scalability runs
  -l, --local-job       Enable ssh-less job runs on the local machine
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

**NOTE:** These dependencies are only need for the non-container running mode.

## Install compilers for Intel X86 platforms
Current version of QaaS relies exclusively on Intel's oneapi software (compiler + MPI) and GNU compilers.
Consequently, these must be installed prior to any use of QaaS on all compute nodes.

Compilers and runtime configuration can be achieved by running the experimental `scripts/setup_compilers.sh` script.
```
cd /<path where qaas git is cloned>/scripts
sudo ./setup_compilers.sh
```

**NOTE:** 
`scripts/setup_compilers.sh` was tested only on `Ubuntu 22.XX` GNU/Linux flavors.

If the compilers configuration step works correctly you should see the following:
```
tree /opt/compilers/
/opt/compilers/
├── gcc
│   ├── gcc-11.4
│   │   └── Linux
│   │       ├── install
│   │       │   ├── g++ -> /usr/bin/g++-11
│   │       │   ├── gcc -> /usr/bin/gcc-11
│   │       │   └── gfortran -> /usr/bin/gfortran-11
│   │       └── intel64
│   │           └── load.sh
│   └── latest -> gcc-11.4
└── intel
    ├── 2023
    │   └── Linux
    │       └── intel64
    │           └── load.sh
    └── latest -> 2023
```
The structure above indicates each compiler has the structure `compiler/<year/version>/Linux/intel64/load.sh` where `load.sh` contains any configuration that will be used (sourced) to load the target software environment. Each `compiler` directory must expose a symbolic link called `latest` pointing to the most recent year/version of that compiler. The `latest` version is used the multi-compiler search procedure. For example, in the sample structure provided above, `latest` points to 2023 and gcc-11.4 for Intel and GNU compilers respectively.
    
**NOTE:** 
Linux Environment Modules can be used/added into `load.sh` files to load compilers and/or parallel runtimes.

**NOTE:**
Current implementation does not support separate loading of the compiler and the MPI runtime. Consequently, `compiler/<year/version>/Linux/intel64/load.sh` must include instructions to the compiler, MPI runtime and eventually any other required library like math libraries. 

## Update qaas.conf configuration
QaaS relies on a global configuration file `qaas/qaas-backplane/config/qaas.conf` to control QaaS runs.
Users must modify the following parameters:
- `QAAS_ROOT`: path to where QaaS runs are stored.
- `QAAS_SCRIPT_ROOT`: path to QaaS scripts root file system so that `$QAAS_SCRIPT_ROOT/qaas-service` is accessible on compute nodes.
- `QAAS_COMPILERS_ROOT_DIRECTORY` : path to QaaS scripts to source compilers and Intel runtime.
- `QAAS_INTEL_COMPILERS_DIRECTORY` : path to Intel compilers and runtimes installation directory. By default, it points to `/opt/intel/oneapi`.
- `QAAS_ENABLED_COMPILERS`: List of compilers to be enabled with QaaS. They must be provisioned/installed.
- `QAAS_USER` : target user name on the compute node for ssh access (password-less must configured
- `QAAS_MACHINES_POOL`: machine name of target node where to perform QaaS runs (localhost by default)

# Running QaaS

In order to perform QaaS runs on a target application, a json specification must be available.
`<path to qaas root>/demo/json_inputs/` contains multiple examples of apps to run.

- Run the QaaS strategizer (only unicore logic for now) using the debug mode but with container mode disabled.
```
cd <path to qaas root>/qaas-backplane/src
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer --no-container -D
is similar to
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer --no-container -D --parallel-compiler-runs off
```
- Use `MPI` to multi-compiler search runs (multicore runs for each tested compiler and compiler flags pair) using as many `MPI` ranks as physical cores are available.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer -p mpi --no-container -D
```
- Use `OpenMP` to multi-compiler search runs (multicore runs for each tested compiler and compiler flags pair) using as many `OpenMP` threads as physical cores are available.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer -p mpi --no-container -D
```
- Use a hybrid `MPI`/`OpenMP` running mode for  multi-compiler search runs. A run is started by setting `MPI` ranks equals to the number of sockets and `OpenMP` threads equals to the number of physical cores per socket.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer -p hybrid --no-container -D
```
- Enable scalability runs in QaaS logic after the multi-compiler search procedure. 
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer -p mpi --enable-parallel-scale --no-container -D
```
- To avoid `ssh` and submit jobs on the local machine.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer --local-job --no-container -D 
```

# Running QaaS in a container

To run QaaS in a container (preferred way), users must follow the steps below:
- Install `podman` (rootless mode).
- Build container image: `container/build-image.sh`
- Pull container image: `podman pull <registery>/qaas:production`
- Setup compiler scripts structure similar to what the `setup_compilers.sh` is doing (see above)
- Run QaaS: `./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer --as-root-in-container -D`

# QaaS backplane limitations
- Hardware support limited to:
    - x86 architectures
    - Intel architectures: tested on SkyLake, IceLake and Sapphire Rapids servers (DDR5 and HBM variants)
- Compiler integration limited to `icx/icpx/ifx` (2022, 2023), `icc/icpc/ifort` (2022) and `gcc/g++/gfortran` (11.x, 12.x)
- `MPI` support limited to `IntelMPI` 
- Tests carried on `Linux/Ubuntu` 22.04
