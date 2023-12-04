#ifndef __REPLAY__H
#define __REPLAY__H

#ifdef __cplusplus
extern "C"
{
#endif

//#include <stdio.h>
// include FILE.h rather than stdio.h to avoid type conflict.
#include <bits/types/FILE.h>
extern int fprintf (FILE *__restrict __stream, const char *__restrict __format, ...);
// The load functions from libcere_replay performs the memory restoration &
// optionally cache warmup. Here are its parameters :
// - char* loopName
// - int InvocationToReplay
// - int number of variable arguments
// - void** array of adresses filled by the replay lib
void load(char *loop_name, int invocation, int count, void *addresses[count]);
void run_loop(FILE* fp, int instance_num, int call_count,int max_seconds);

// from rdtsc.h of cere
static __inline__ unsigned long long int rdtsc() {
    unsigned long long int a, d;

#if defined(__amd64__)
    __asm__ volatile ("rdtsc" : "=a" (a), "=d" (d));
    return (d<<32) | a;
#elif defined(__aarch64__)
    __asm__ volatile("mrs %0, cntvct_el0" : "=r" (a));
    return a;
#endif
}
#ifdef __cplusplus
}
#endif

#endif /* REPLAY__H */
