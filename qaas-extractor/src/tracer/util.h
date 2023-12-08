enum pointsTo { heapPointerData, stackPointerData, globalPointerData };
#ifdef __cplusplus
extern "C" {
#endif

// check whether current thread/mpi process match given omp_thread and mpi_rank
int check_omp_mpi_id(int omp_thread, int mpi_rank);

static void *alignAddress(void *addr, int align);
void writeDataRangeToFile(char *addressDataFile, unsigned char *dumpArrayMin,
                          unsigned char *dumpArrayMax, int memoryLocation);
void *my_mallocMemoryChunkInclusive(char *fileName, void *startAddr,
                                    void *endAddr);
void *my_mallocMemoryChunk(char *fileName, void *startAddr, void *endAddr,
                           unsigned long long size);
void readDataFromFile(char *addressDataFile, unsigned char *dumpArray,
                      int size);
void readDataRangeFromFile(char *addressDataFile, unsigned char *dumpArrayMin,
                           unsigned char *dumpArrayMax);
// static inline __attribute__((always_inline)) void asm_basepointer(void*
// basepointer); static inline __attribute__((always_inline)) void
// asm_stackpointer(void* stackpointer);
static inline __attribute__((always_inline)) void
asm_basepointer(void *basepointer) {
    __asm__("movq %%rbp, %0" : "=m"(basepointer));
}

static inline __attribute__((always_inline)) void
asm_stackpointer(void *stackpointer) {
    __asm__("movq %%rsp, %0" : "=m"(stackpointer));
}

#ifdef __cplusplus
}
#endif
