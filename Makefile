ifeq ($(OS), centos)
	CC = g++-4.9
	FLAGS = -std=c++14 -g -DOS_CENTOS

	ROSE_PATH = ${CURDIR}/tools/rose_build
	FLAGS += -DROSE_PATH=$(ROSE_PATH)
	BOOST_PATH = ${CURDIR}/tools/boost_build
	ROSE_INCLUDE = -I${ROSE_PATH}/include/ -I${BOOST_PATH}/include/
	ROSE_LIB = -lROSE_DLL
else
	CC = g++
	FLAGS = -std=c++14 -g

	ROSE_PATH = /usr/rose
	#BOOST_PATH = ${CURDIR}/tools/boost_build
	ROSE_INCLUDE = -I${ROSE_PATH}/include/rose #-I${BOOST_PATH}/include/
	ROSE_LIB = -L${JAVA_HOME}/lib -lrose
endif

OBJS = obj
BIN  = bin

EXTRACTOR_PATH    = src/extractor
DRIVER_PATH       = src/driver

TRACER_PATH		  = src/tracer

LE_DATA_FOLDER    = /tmp/LoopExtractor_data

DIRS := $(shell mkdir -p ${CURDIR}/$(OBJS) &&  mkdir -p ${CURDIR}/$(BIN))
  
all: driver

##### EXTRACTOR #####
EXTRACTOR_COMPILE_FLAGS = -I${CURDIR}/src $(ROSE_INCLUDE)
EXTRACTOR_LD_FLAGS = -L${ROSE_PATH}/lib \
                     $(ROSE_LIB) \
                     -lboost_system  -lboost_chrono -lquadmath
                     #-L${BOOST_PATH}/lib \
                     #-lboost_iostreams -lboost_system

OBJ_EXTRACTOR = $(OBJS)/extractor.o
SRC_EXTRACTOR  = $(EXTRACTOR_PATH)/extractor.cpp 
INC_EXTRACTOR  = $(EXTRACTOR_PATH)/extractor.h 
OBJ_COMMON = $(OBJS)/common.o

extractor: $(OBJ_EXTRACTOR) $(OBJ_COMMON)

$(OBJ_EXTRACTOR): $(SRC_EXTRACTOR) $(INC_EXTRACTOR) $(INC_TRACER)
	$(CC) $(FLAGS) $(EXTRACTOR_COMPILE_FLAGS) $(SRC_EXTRACTOR) -c -o $@

$(OBJ_COMMON): src/driver/common.cpp
	$(CC) $(FLAGS) src/driver/common.cpp $(ROSE_INCLUDE) -c -o $@

##### TRACER #####
TRACER_COMPILE_FLAGS = -I${CURDIR}/src $(ROSE_INCLUDE)
TRACER_LD_FLAGS = -L${ROSE_PATH}/lib \
                     $(ROSE_LIB) \
                     -lboost_system  -lboost_chrono -lquadmath
                     #-L${BOOST_PATH}/lib \
                     #-lboost_iostreams -lboost_system

OBJ_TRACER = $(OBJS)/tracer.o
SRC_TRACER  = $(TRACER_PATH)/tracer.cpp 
INC_TRACER  = $(TRACER_PATH)/tracer.h
OBJ_COMMON = $(OBJS)/common.o

tracer: $(OBJ_TRACER) $(OBJ_COMMON)

$(OBJ_TRACER): $(SRC_TRACER) $(INC_TRACER)
	$(CC) $(FLAGS) $(TRACER_COMPILE_FLAGS) $(SRC_TRACER) -c -o $@


##### DRIVER #####

DRIVER_COMPILE_FLAGS = $(EXTRACTOR_COMPILE_FLAGS) $(OPENCV_INCLUDE)
DRIVER_LD_FLAGS      = -L${JAVA_HOME}/lib/server -ljvm $(EXTRACTOR_LD_FLAGS) -pthread $(PREDICTOR_LD_FLAGS)

OBJ_DRIVER = $(OBJS)/driver.o
SRC_DRIVER = $(DRIVER_PATH)/driver.cpp 

#driver: $(OBJ_DRIVER) $(OBJ_EXTRACTOR) $(OBJ_TRACER) $(OBJ_COMMON) 
#	$(CC) $^ $(DRIVER_LD_FLAGS) -o $(BIN)/LoopExtractor

driver: $(OBJ_DRIVER) $(OBJ_EXTRACTOR) $(OBJ_COMMON) 
	$(CC) $^ $(DRIVER_LD_FLAGS) -o $(BIN)/LoopExtractor

$(OBJ_DRIVER): $(SRC_DRIVER)
	$(CC) $(FLAGS) $(DRIVER_COMPILE_FLAGS) $(SRC_DRIVER) -c -o $@

##### CLEAN #####
clean:
	rm -f $(OBJS)/* $(BIN)/*
clean_data_folder:
	rm -rf $(LE_DATA_FOLDER)
  
.PHONY: all dirs extractor tracer driver clean
