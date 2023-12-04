cmake_minimum_required(VERSION 3.2.0)
project(restore_clover_leaf)
find_package(OpenMP REQUIRED)
# include_directories(src)
if(OPENMP_FOUND)
    message("OPENMP FOUND")
endif()
# target_link_libraries()
# add_subdirectory(sub_test)
add_executable(restore_clover_leaf "src/util.c"
        "src/restore.cc"
        "src/util.c"
        "src/clover_clover_exchange_line84_localdiskcwong29workingcodelet_extractor_workCloverLeaf_cmakesrc.cc"	)
target_include_directories(restore_clover_leaf PRIVATE include)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")#-DDEFINED_IN_CMAKELISTS -profile-functions -profile-loops=all -loop-report=2# COMPILER=INTEL USE_OPENMP=1
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
# generate cmakefiles cmakecache.txt cmake_install.cmake Makefile

# MPI_CC_INTEL = mpiicpc
# MPI_CC_GNU = mpic++
# CC_CUDA = nvcc_wrapper
# CC_CUDA_CLANG = clang++
# MPI_CC_ = mpic++



# FLAGS_GNU = -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -no-pie -fcf-protection=none
# FLAGS_INTEL = -std=c++11 -O3 -g -restrict -march=native -fp-model strict
# # FLAGS_INTEL = -std=c++11 -O3 -ipo -restrict -xMIC-AVX512 -no-prec-div -fno-alias
# # FLAGS_INTEL = -std=c++11 -O3 -ipo -restrict -no-prec-div -fno-alias
# FLAGS_CUDA = 
# FLAGS_ = 

# MPI_FLAGS = $(FLAGS_$(COMPILER))
# MPI_CC = $(MPI_CC_$(COMPILER))

# OBJECTS = data_c.o \
# 	definitions_c.o \
# 	report.o \
# 	generate_chunk.o \
# 	ideal_gas.o \
# 	timer_c.o \
# 	viscosity.o \
# 	calc_dt.o \
# 	PdV.o \
# 	revert.o \
# 	flux_calc.o \
# 	advection.o \
# 	reset_field.o \
# 	visit.o \
# 	update_halo.o \
# 	accelerate.o \
# 	field_summary.o

# MPIOBJECTS = initialise.o \
# 	hydro.o \
# 	timestep.o \
# 	start.o \
# 	clover.o



# default: build

# ifdef USE_KOKKOS
#     ifeq ($(USE_KOKKOS),gpu)
#         CXX = ${KOKKOS_PATH}/bin/nvcc_wrapper
#         MPI_FLAGS += -lcudart
#         FLAGS := $(FLAGS) -O3

#         MPI_FLAGS += $(shell mpic++ --showme:compile)
#         MPI_FLAGS += $(shell mpic++ --showme:link)

#         MPI_CC = $(CXX)

#         KOKKOS_CUDA_OPTIONS = "enable_lambda"
#         KOKKOS_DEVICE= "Cuda"
#     else
#         CXX = $(MPI_CC)
#         FLAGS += $(MPI_FLAGS)
#     endif
#     MPI_FLAGS += -DUSE_KOKKOS
#     FLAGS += -DUSE_KOKKOS
#     CC = $(CXX)
#     include $(KOKKOS_PATH)/Makefile.kokkos

#     ifeq ($(COMPILER),GNU)
#       MPI_FLAGS += -fopenmp
#     endif
# endif

# ifdef USE_OMPSS
#     CC = mcc
#     FLAGS += --ompss $(MPI_FLAGS) -DUSE_OMPSS
#     MPI_FLAGS += --ompss -DUSE_OMPSS
# endif

# ifdef USE_OPENMP
#     CC = $(MPI_CC)
    
#     FLAGS += -fopenmp $(MPI_FLAGS) -DUSE_OPENMP
#     MPI_FLAGS += -fopenmp -DUSE_OPENMP
# endif

# ifdef USE_OPENCL
#     CC = $(MPI_CC)

#     ifeq ($(shell uname),Darwin)
#         MPI_FLAGS += -framework OpenCL -DUSE_OPENCL
#     else
#         MPI_FLAGS += -lOpenCL -DUSE_OPENCL
#     endif
#     FLAGS += $(MPI_FLAGS)
# endif

# ifdef USE_CUDA
#     CC = nvcc

#     MPI_FLAGS += -DUSE_CUDA \
#         -L/nfs/modules/cuda/7.5.18/lib64 -lcudart

#     FLAGS += -x cu -O3 -std=c++11 -DUSE_CUDA \
#         -I/nfs/modules/openmpi/1.10.3/include
# endif
# ifdef USE_CUDA_CLANG
#     CC = clang++

#     MPI_FLAGS += -DUSE_CUDA \
#         -L/nfs/modules/cuda/7.5.18/lib64 -lcudart

#     FLAGS += -x cuda --cuda-gpu-arch=sm_35 -ffp-contract=fast  -ffast-math -O3 -std=c++11 -DUSE_CUDA \
#         -I/nfs/modules/openmpi/1.10.3/include
# endif

# OBJDIR    = obj
# MPIOBJDIR = mpiobj
# SRCDIR    = src

# _OBJECTS = $(addprefix $(OBJDIR)/, $(OBJECTS))
# _SOURCES = $(addprefix $(SRCDIR)/, $(OBJECTS:.o=.cc))
# _MPIOBJECTS = $(addprefix $(MPIOBJDIR)/, $(MPIOBJECTS))
# _MPISOURCES = $(addprefix $(SRCDIR)/, $(MPIOBJECTS:.o=.cc))

# # -include $(_OBJECTS:.o=.d)
# # -include $(_MPIOBJECTS:.o=.d)

# depend:
# 	makedepend -- $(FLAGS) -- $(_SOURCES) $(_MPISOURCES)

# build: $(_OBJECTS) $(_MPIOBJECTS) Makefile $(KOKKOS_LINK_DEPENDS) $(KERNELS)
# 	$(MPI_CC) $(MPI_FLAGS) $(KOKKOS_CPPFLAGS) $(EXTRA_PATH) $(_OBJECTS) $(_MPIOBJECTS) $(SRCDIR)/clover_leaf.cc $(KOKKOS_LIBS) $(KOKKOS_LDFLAGS) -o clover_leaf

# $(OBJDIR)/%.o: $(SRCDIR)/%.cc $(KOKKOS_CPP_DEPENDS)
# 	$(CC) $(FLAGS) $(MPIINCLUDE) $(KOKKOS_CPPFLAGS) $(KOKKOS_CXXFLAGS) $(EXTRA_INC) -c $< -o $@
# 	# $(CC) $(FLAGS) $(MPIINCLUDE) $(KOKKOS_CPPFLAGS) $(KOKKOS_CXXFLAGS) $(EXTRA_INC) -MM $< > $(OBJDIR)/$*.d

# $(MPIOBJDIR)/%.o: $(SRCDIR)/%.cc $(KOKKOS_CPP_DEPENDS)
# 	$(MPI_CC) $(MPI_FLAGS) $(KOKKOS_CPPFLAGS) $(EXTRA_INC) -c $< -o $@
# 	# $(MPI_CC) $(MPI_FLAGS) $(KOKKOS_CPPFLAGS) $(EXTRA_INC) -MM $< > $(MPIOBJDIR)/$*.d


# fast: $(_SOURCES) $(_MPISOURCES) Makefile $(KOKKOS_LINK_DEPENDS) $(KERNELS)
# 	$(MPI_CC) $(MPI_FLAGS) $(KOKKOS_CPPFLAGS) $(EXTRA_PATH) $(_SOURCES) $(_MPISOURCES) $(SRCDIR)/clover_leaf.cc $(KOKKOS_LIBS) $(KOKKOS_LDFLAGS) -o clover_leaf
# 	# $(MPI_CC) $(MPI_FLAGS) $(KOKKOS_CPPFLAGS) $(EXTRA_PATH) $(_SOURCES) $(_MPISOURCES) $(SRCDIR)/clover_leaf.cc $(KOKKOS_LIBS) $(KOKKOS_LDFLAGS) -o clover_leaf

# clean: 
# 	rm -f $(OBJDIR)/* $(MPIOBJDIR)/* *.o clover_leaf

# print-%  : ; @echo $* = $($*)# DO NOT DELETE
