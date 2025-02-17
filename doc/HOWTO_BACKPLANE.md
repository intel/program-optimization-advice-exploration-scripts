# QaaS CLI
Using QaaS CLI (backplane scripts)
```
git clone <this repo>
cd qaas/qaas-backplane/src
./qaas.py --help
usage: qaas.py [-h] -ap <input-file> [-D | -q] [-wc] [-rc] [-ncd] [-ncf] [-p {auto,off,mpi,openmp,hybrid}] [-s [{best-compiler,full}]] [-r] [-o <reports-dir>]

This is QaaS backend service.

options:
  -h, --help            show this help message and exit
  -ap <input-file>, --app-params <input-file>
                        name the input file (including suffix)
  -D, --debug           debug mode
  -q, --quiet           quiet mode
  -wc, --with-container
                        Enable container mode (Experimental).
  -rc, --as-root-in-container
                        Run host users as root in container [permissive rootless mode in podman] (Experimental). Not allowed for true root users.
  -ncd, --no-compiler-default
                        Disable search for best default compiler
  -ncf, --no-compiler-flags
                        Disable search for best compiler flags
  -p {auto,off,mpi,openmp,hybrid}, --parallel-compiler-runs {auto,off,mpi,openmp,hybrid}
                        Force multiprocessing [auto, MPI, OpenMP or hybrid] for compiler search runs
  -s [{best-compiler,full}], --enable-parallel-scale [{best-compiler,full}]
                        Turn on multicore scalability runs (optional). If not set, default is no scalability runs. If set, option is 'full' by default to runs scalability runs for each
                        compiler. If set with 'best-compiler', scalability runs only using best compiler/options
  -r, --remote-job      Enable qaas job runs on a remote machine (QAAS_MACHINES_POOL variable in qaas.conf) through ssh
  -o <reports-dir>, --output-dir <reports-dir>
                        base directory where to put generated QaaS reports. Default is <launch_dir>/qaas_out/
```

# Configuration

## Install system dependencies
```
sudo apt-get install -y git git-lfs python3-pip numactl cmake ninja-build
```

## Install python dependencies
```
pip3 install pytrie numpy py-cpuinfo pandas slpp sqlalchemy luadata
```
Alternatively, all python dependencies can be fulfilled through virtual environment
```
python3 -m venv venv/aarch64
pip3 install pytrie numpy py-cpuinfo pandas slpp sqlalchemy luadata
source venv/aarch64/bin/activate
./qaas.py <qaas run command>
deactivate
```

**NOTE:** These dependencies are only need for the non-container running mode.

## Supported compilers per vendor
- Intel:
  - icx/icpx/ifx
  - icc/icpc/ifort
  - gcc/g++/gfortran
- AMD
  - AOCCclang/AOCCclang++/AOCCflang
  - gcc/g++/gfortran
  - icx/icpx/ifx
- AARCH64
  - ARMclang/ARMclang++/ARMflang
  - gcc/g++/gfortran
  - icx/icpx/ifx

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
│   │   ├── install
│   │   │   ├── g++ -> /usr/bin/g++-11
│   │   │   ├── gcc -> /usr/bin/gcc-11
│   │   │   └── gfortran -> /usr/bin/gfortran-11
│   │   └── env 
│   │       └── load.sh
│   └── latest -> gcc-11.4
└── intel
    ├── 2023
    │   └── env
    │       └── load.sh
    └── latest -> 2023
```
The structure above indicates each compiler has the structure `compiler/<year/version>/env/load.sh` where `load.sh` contains any configuration that will be used (sourced) to load the target software environment. Each `compiler` directory must expose a symbolic link called `latest` pointing to the most recent year/version of that compiler. The `latest` version is used the multi-compiler search procedure. For example, in the sample structure provided above, `latest` points to 2023 and gcc-11.4 for Intel and GNU compilers respectively.
    
**NOTE:** 
Linux Environment Modules can be used/added into `load.sh` files to load compilers and/or parallel runtimes.

**NOTE:**
Current implementation does not support separate loading of the compiler and the MPI runtime. Consequently, `compiler/<year/version>/env/load.sh` must include instructions to the compiler, MPI runtime and eventually any other required library like math libraries. 

## Install compilers for AMD x86\_64 and AARCH64 platforms
- Install target compiler if does not exist
- Identify installation path
- Create a structure `compiler/<year/version>/env/load.sh`  similar the one showed for Intel X86.

## Update qaas.conf configuration
QaaS relies on a global configuration file `qaas/qaas-backplane/config/qaas.conf` to control QaaS runs.
Users must modify the following parameters:
- `QAAS_ROOT`: path to where QaaS runs are stored.
- `QAAS_SCRIPT_ROOT`: path to QaaS scripts root file system so that `$QAAS_SCRIPT_ROOT/qaas-service` is accessible on compute nodes.
- `QAAS_COMPILERS_ROOT_DIRECTORY` : path to QaaS scripts to source compilers and Intel runtime.
- `QAAS_INTEL_COMPILERS_DIRECTORY` : path to Intel compilers and runtimes installation directory. By default, it points to `/opt/intel/oneapi`. Required only in container mode if compiler version installed in container is not the right one (to be deprecated).
- `QAAS_GNU_COMPILERS_DIRECTORY` : path to GNU compilers and runtimes installation directory. Required only in container mode if compiler version installed in container is not the right one (to be deprecated).
- `QAAS_ENABLED_COMPILERS`: List of compilers to be enabled with QaaS. They must be provisioned/installed. Valid values are icx,icc,gcc on Intel platforms, aocc,icx,gcc on AMD platforms and armclang,gcc on ARM platforms
- `QAAS_USER` : target user name on the compute node for ssh access (password-less must configured.
- `QAAS_MACHINES_POOL`: machine name of target node where to perform QaaS runs (localhost by default).
- `QAAS_DEFAULT_REPETITIONS`: controls the number of runs of the initial profiling run to asses performance stability and quality (default to 11 runs).
- `QAAS_MAX_ALLOWED_EXEC_TIME`: controls the time limit in seconds of the initial profiling run. Set to 3 minutes by default.

# Running QaaS

## Application's JSON specification
In order to perform QaaS runs on a target application, a json specification must be available.
`<path to qaas root>/demo/json_inputs/` contains multiple examples of apps to run. The JSON file consists of 4 main sections:
- Account: specifies the organization/owner of the code. Account information is provided through the `QAAS_ACCOUNT` variable
- Application: provides technical information about the application name, how to get the code and how to run it:
- Compiler info: user provides information about his compiler of choice and any default compilation flags that are not set in his cmake recipe
- Runtime: specify if MPI or OpenMP are supported by the application and what type of scaling: strong vs weak

The `<path to qaas root>/demo/json_inputs/` provides two examples. Let us take a look at `demo/json_inputs/input-miniqmc.json`

```
{
    "account": {
        "QAAS_ACCOUNT": "intel"
    },
    "application": {
        "APP_NAME": "miniqmc",
        "GIT": {
            "USER":   "",
            "TOKEN":  "",
            "BRANCH": "OMP_offload",
            "SRC_URL": "https://github.com/jngkim/miniqmc.git",
            "DATA_USER":   "",
            "DATA_TOKEN":  "",
            "DATA_URL": "",
            "DATA_BRANCH": "",
            "DATA_DOWNLOAD_PATH": ""
        },
        "RUN": {
            "APP_RUN_CMD": "<binary> -g \\\"2 2 1\\\" -b",
            "FOM_REGEX": "'(?<=Total throughput \\( N_walkers \\* N_elec\\^3 / Total time \\) \\=).*'",
            "FOM_TYPE": "RATE",
            "FOM_UNIT": "N_elec/s",
            "APP_ENV_MAP": { }
        }
    },
    "compiler": {
        "USER_CC": "MPI-icx",
        "USER_CC_VERSION": "latest",
        "USER_C_FLAGS": "",
        "USER_CXX_FLAGS": "-cxx=icpx -O3 -march=native",
        "USER_FC_FLAGS": "",
        "USER_LINK_FLAGS": "",
        "USER_EXTRA_CMAKE_FLAGS": "-DENABLE_OFFLOAD=0 -DQMC_MPI=1",
        "USER_TARGET": "miniqmc",
        "USER_TARGET_LOCATION": "bin/miniqmc"
    },
    "runtime": {
        "MPI": "weak",
        "OPENMP": "weak"
    }
}
```
### "account" section
Provides information about the QaaS runner.Consists only of `QAAS_ACCOUNT` variable

### "application" section
Requires 3 sub-domains:
1. `APP_NAME`: name of the application to put in created directories structure and runs reports
2. `GIT`: dictionary of items specifying what git repository to use to get the code and and data alongside all authentication (optional) information
   - `USER`: user name to use (optional) to access git repository of the source code
   - `TOKEN`: private TOKEN (optional) to access git repository of the source code
   - `BRANCH`: branch name to use in source code repository. If empty, it defaults to `master`
   - `SRC_URL`: URL of the git repository of source code (required)

   - `DATA_USER`: user name to use (optional) to access git repository of the data input
   - `DATA_TOKEN`: private TOKEN (optional) to access git repository of the data input
   - `DATA_URL`: URL (optional) of the git repository of data input
   - `DATA_BRANCH`: branch name (optional) to use in data input git repository. If empty, it defaults to `master`
   - `DATA_DOWNLOAD_PATH`: relative path in data input git repository to pull only a subset of files (optional)
3. `RUN`: specifies run command, extra environment variables and Figure-of-Merit (FOM) scan.
   - `APP_RUN_CMD`: provides the run command on how to run the application. It has always the form `<binary> [application run options]`, where `<binary>` is a keyword which gets renamed at runtime to the actual name of the generated binary
   - `FOM_REGEX`: regular expression (Perl syntax) to capture any exposed FOM by the application  (optional)
   - `FOM_TYPE`: type of FOM metric, RATE (throughput) vs TIME (optional)
   - `FOM_UNIT`: unit used by FOM (optional)
   - `APP_ENV_MAP`: list of extra environment variables. Syntax is JSON dictionary "VAR":"VALUE"

### "compiler" section
Provides information on default compiler and any compilation flags needed to build the target code.
- `USER_CC`: provides user's default compiler. It has the form `[MPI-]<compiler>` where the keyword `MPI` (optional) specifies the need of a MPI compiler wrapper and `<compiler>` represents the actual user choice like icx or gcc.
- `USER_CC_VERSION`: version to use for default compiler. See the configuration section for more information
- `USER_C_FLAGS`: optional C compilation flags
- `USER_CXX_FLAGS"`: optional C++ compilation flags
- `USER_FC_FLAGS`: optional Fortran compilation flags
- `USER_LINK_FLAGS`: optional linker flags
- `USER_EXTRA_CMAKE_FLAGS`: optional extra CMAKE options and variables
- `USER_TARGET`: name of the cmake target binary
- `USER_TARGET_LOCATION`: location of the generated target binary

### "runtime" section
Optional section to indicate what parallelism runtime is present and what scaling mode the application implements.
- `MPI`: indicates whether the application has MPI support and what scaling mode. The supported values are:
   - `no`: no MPI support in the application
   - `strong`: application has MPI support and implements a strong scaling mode
   - `weak`: application has MPI support and implements a weak scaling mode
- `OpenMP`: indicates whether the application has OpenMP support and what scaling mode. The supported values are:
   - `no`: no OpenMP support in the application
   - `strong`: application has OpenMP support and implements a strong scaling mode
   - `weak`: application has OpenMP support and implements a weak scaling mode

## CLI examples
Parallel runs are enabled by default if MPI and/or OpenMP runtimes are specified in the application's JSON specification even if the `-p` option is not specified. The QaaS default mode for compiler exploration is `auto`. Parallel runs are enabled according to the following configurations:
  * Application has MPI and OpenMP (`-p hybrid`): number of ranks equals number of NUMA nodes and number of OpenMP threads per node is number of cores per NUMA node.
  * Application has only MPI: number of ranks equals number of physical cores.
  * Application has only OpenMP: number of OpenMP threads equals number of physical cores.

- Run the QaaS logic (multi-compilers analysis) using the debug mode.
```
cd <path to qaas root>/qaas-backplane/src
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -D
is similar to
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -D --parallel-compiler-runs auto
```
- Use `MPI` to multi-compiler search runs (multicore runs for each tested compiler and compiler flags pair) using as many `MPI` ranks as physical cores are available.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -p mpi -D
```
- Use `OpenMP` to multi-compiler search runs (multicore runs for each tested compiler and compiler flags pair) using as many `OpenMP` threads as physical cores are available.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -p openmp -D
```
- Use a hybrid `MPI`x`OpenMP` running mode for  multi-compiler search runs. A run is started by setting `MPI` ranks equals to the number of NUMA nodes and `OpenMP` threads equals to the number of physical cores per NUMA node.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -p hybrid -D
```
- Enable scalability runs in QaaS logic after the multi-compiler search procedure. This option enables scalability runs for each per-compiler best option.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -p mpi --enable-parallel-scale -D
```
- Enable scalability runs in QaaS logic after the multi-compiler search procedure only for the best compiler.
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -p mpi --enable-parallel-scale best-compiler -D
```
- Enable QaaS unicore runs if no MPI or OpenMP parallelism exposed by the application
```
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -p off -D
is similar to
./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json -D
```

# Running QaaS in a container

To run QaaS in a container (not well tested mode), users must follow the steps below:
- Install `podman` (rootless mode).
- Build container image: `container/build-image.sh`
- Pull container image: `podman pull <registery>/qaas:production`
- Setup compiler scripts structure similar to what the `setup_compilers.sh` is doing (see above)
- Run QaaS: `./qaas.py -ap ../../demo/json_inputs/input-miniqmc.json --logic strategizer --as-root-in-container -D`

# QaaS backplane limitations
- Application build engine relies on CMAKE
- `MPI` support limited to `IntelMPI` and `OpenMPI`
- Tests carried on `Linux/Ubuntu` 22.04
- No integration with (HPC clusters) Workload Mangers like SLURM. QaaS backplane must be run as normal job
- No support for multi-nodes (HPC clusters) runs
