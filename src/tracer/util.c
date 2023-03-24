#include <assert.h>
#include <fcntl.h>
#include <malloc.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <omp.h>
#include <mpi.h>

#include "defs.h"
#include "util.h"


// check whether current thread/mpi process match given omp_thread and mpi_rank
int check_omp_mpi_id(int omp_thread, int mpi_rank) {
  int my_mpi_rank = 0;
  int my_omp_thread = 0;
#ifdef _OPENMP
  my_omp_thread = omp_get_thread_num();
#endif
  MPI_Comm_rank(MPI_COMM_WORLD, &my_mpi_rank);
  int answer = (my_mpi_rank == mpi_rank) && (my_omp_thread == omp_thread);
  if (answer)
  	printf("my:(mpi=%d, omp=%d); match:(mpi=%d, omp=%d)\n", my_mpi_rank, my_omp_thread, mpi_rank, omp_thread);

  return answer;
}

/*
 * write heap/stack/global data to disk in binary format
 */
void writeDataToFile(char *addressDataFile, unsigned char *dumpArray, int size,
                     int memoryLocation) {

    size_t len = strlen(addressDataFile);
    char *heapDataFile = malloc(len + 4);
    strcpy(heapDataFile, addressDataFile);
    heapDataFile[len] = '.';
    if (memoryLocation == heapPointerData) {
        heapDataFile[len + 1] = 'h';
        heapDataFile[len + 2] = 'd';
    } else if (memoryLocation == stackPointerData) {
        heapDataFile[len + 1] = 's';
        heapDataFile[len + 2] = 't';
    } else if (memoryLocation == globalPointerData) {
        heapDataFile[len + 1] = 'g';
        heapDataFile[len + 2] = 'l';
    } else {
        printf("undefined memory location!");
        exit(1);
    }
    heapDataFile[len + 3] = '\0';

    FILE *pFile = fopen(heapDataFile, "w");

    fwrite(dumpArray, sizeof(unsigned char), size, pFile);
    fclose(pFile);

    struct stat sbuf;
    if (stat(heapDataFile, &sbuf) == -1) {
        perror("stat");
        exit(1);
    }

    free(heapDataFile);
}

void readDataFromFile(char *addressDataFile, unsigned char *dumpArray,
                      int size) {
    FILE *pFile = fopen(addressDataFile, "r");
    int sz = fread(dumpArray, sizeof(unsigned char), size, pFile);
    printf("sz=%d, size=%d\n", sz, size);
    assert(sz == size);
    fclose(pFile);
}

void *my_mallocMemoryChunk(char *fileName, void *startAddr, void *endAddr,
                           unsigned long long size) {

    void *volatile p = malloc(1);
    free(p);
    // Note: must set brk to the maxLoc of heap before any
    // malloc/callloc/realloc otherwise, the data between the minLoc and maxLoc
    // of the original heap would be overwritten. It will result in segmentation
    // fault.
    void *oldBrk = sbrk(0);

    unsigned long long unsingedExtendEndAddr =
        (unsigned long long)startAddr + size * 2;
    void *extendEndAddr = (void *)unsingedExtendEndAddr;
    void *alignedEndAddr = alignAddress(extendEndAddr, ALIGNEDTO);

    if (brk(alignedEndAddr) == -1) {
        perror("brk failed in mallocMemoryChunk: ");
    }

    char *buffer = (void *)(endAddr + HEAPOFFSET);
    buffer = (char *)alignAddress(buffer, ALIGNEDTO);

    // cannot use fopen here because fopen calls malloc internally. We are
    // unable to control the brk inside of fopen. For example, malloc might find
    // an address which is not on the top of the heap we intentionally extended.
    // Instead, it allocates the file pointer to an address which first fits the
    // size of the pointer. There would be a problem when we call fclose because
    // it is going to free the allocated space. To solve the problem, we could
    // just use open and read.
    int input_fd = open(fileName, O_RDONLY);
    if (input_fd == -1) {
        perror("open heap file failed");
        exit(2);
    }

    unsigned long long result;
    // printf("Has11 %llu, address of buffer: %p, %c\n", size, buffer,
    // buffer[0]);
    result = read(input_fd, buffer, size);
    if (result != size) {
        printf("Has %llu, read %llu, address of buffer: %p\n", size, result,
               buffer);
        perror("Reading file error");
        exit(3);
    }

    memcpy(startAddr, buffer, size);

    close(input_fd);

    return oldBrk;
}

void *my_mallocMemoryChunkInclusive(char *fileName, void *startAddr,
                                    void *endAddr) {
    if (startAddr == endAddr) {
        // printf("NOTHING TO ALLOCATE\n");
        return;
    }
    unsigned char *endAddrPlusOne = endAddr + 1;
    unsigned long long size = endAddrPlusOne - (unsigned char *)startAddr;

    return my_mallocMemoryChunk(fileName, startAddr, endAddrPlusOne, size);
}

void writeDataRangeToFile(char *addressDataFile, unsigned char *dumpArrayMin,
                          unsigned char *dumpArrayMax, int memoryLocation) {
    if (dumpArrayMax == dumpArrayMin && dumpArrayMin == 0) {
        // printf("NOTHING TO WRITE!!!\n");
        return;
    }
    int size = dumpArrayMax - dumpArrayMin + 1;
    printf("%p, %p, %d\n", dumpArrayMin, dumpArrayMax, size);
    writeDataToFile(addressDataFile, dumpArrayMin, size, memoryLocation);
}
void readDataRangeFromFile(char *addressDataFile, unsigned char *dumpArrayMin,
                           unsigned char *dumpArrayMax) {
    if (dumpArrayMax == dumpArrayMin && dumpArrayMin == 0) {
        // printf("NOTHING TO READ!!!\n");
        return;
    }
    int size = dumpArrayMax - dumpArrayMin + 1;
    // printf("%p, %p, %d\n", dumpArrayMin, dumpArrayMax, size);
    readDataFromFile(addressDataFile, dumpArrayMin, size);
}

static void *alignAddress(void *addr, int align) {
    uintptr_t mask = align - 1;
    void *alignedAddr = (void *)(((uintptr_t)addr + mask) & ~mask);

    return alignedAddr;
}
