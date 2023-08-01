#ifndef __REPLAY__H
#define __REPLAY__H

#ifdef __cplusplus
extern "C"
{
#endif
// The load functions from libcere_replay performs the memory restoration &
// optionally cache warmup. Here are its parameters :
// - char* loopName
// - int InvocationToReplay
// - int number of variable arguments
// - void** array of adresses filled by the replay lib
void load(char *loop_name, int invocation, int count, void *addresses[count]);
void run_loop(int instance_num, int call_count,int max_seconds);
#ifdef __cplusplus
}
#endif

#endif /* REPLAY__H */
