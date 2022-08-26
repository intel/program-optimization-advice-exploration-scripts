/*
 * defs.h
 *
 *  Created on: Mar 19, 2016
 *      Author: zhi
 */

#ifndef DEFS_H_
#define DEFS_H_

#define SUCCESS true
#define FAIL false
#define PRINTIMMEDIATELY true
#define PRINTLATER false

#define MEMORYOFFSET 0x01

#define HEAPOFFSET 0x10

#define EXTENDSIZE 0x10

#define STACK_BOTTOM_ADDRESS 0x7fffffffefff

#define RESERVEDSTACKSPACE                                                     \
  0x400 // reserve 1K for the local variable in the main function of the
        // isolated loop

#define RESERVEDDATASEGSPACE 0x100000 // reserve 1M for data segment

#define PAGESIZE 0x1000

#define STACKSIZE 0x800000 // default max stack size is 8M

#define ALIGNEDTO 0x08 // align address to 8 bytes

#endif /* DEFS_H_ */
