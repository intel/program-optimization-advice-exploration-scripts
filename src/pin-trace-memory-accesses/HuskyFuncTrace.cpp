/*
 * Copyright (C) 2004-2021 Intel Corporation.
 * SPDX-License-Identifier: MIT
 */

/*! @file
 *  This file contains an ISA-portable PIN tool for tracing instructions
 */

#include "pin.H"
#include <iostream>
#include <fstream>
#include <string>
#include <set>
using std::cerr;
using std::endl;
using std::hex;
using std::dec;
using std::ios;
using std::string;
using std::set;

/* ===================================================================== */
/* Global Variables */
/* ===================================================================== */

std::ofstream* TraceFile;

std::set<ADDRINT> addrset;
std::set<ADDRINT> escape_addrset;

ADDRINT startDataSegAddr = 0;
ADDRINT endDataSegAddr = 0;
ADDRINT startHeapSegAddr = 0;
ADDRINT endHeapSegAddr = 0;
ADDRINT startStackSegAddr = 0;
ADDRINT endStackSegAddr = 0;

ADDRINT minDataSegAddr = 0;
ADDRINT maxDataSegAddr = 0;
ADDRINT minHeapSegAddr = 0;
ADDRINT maxHeapSegAddr = 0;
ADDRINT minStackSegAddr = 0;
ADDRINT maxStackSegAddr = 0;

std::string loopFuncName;
std::string callGraphFileName;
int counting = 0;
unsigned long long escaped_access_count = 0;

std::ostream* out = &cerr;

set<string>  funcNames;
set<ADDRINT> funcAddresses;
unsigned long long level = 0;
unsigned long long instance_id = 0;

/* ===================================================================== */
/* Commandline Switches */
/* ===================================================================== */
KNOB< string > KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "", "specify file name for HuskyTool output");

KNOB< BOOL > KnobCount(KNOB_MODE_WRITEONCE, "pintool", "count", "1",
                       "count instructions, basic blocks and threads in the application");

KNOB< ADDRINT > KnobStartDataSegAddr(KNOB_MODE_WRITEONCE, "pintool", "start_ds_addr", "0x0", "specify start address of data segment");
KNOB< ADDRINT > KnobEndDataSegAddr(KNOB_MODE_WRITEONCE, "pintool", "end_ds_addr", "0x0", "specify end address of data segment");
KNOB< ADDRINT > KnobStartHeapSegAddr(KNOB_MODE_WRITEONCE, "pintool", "start_heap_addr", "0x0", "specify start address of heap segment");
KNOB< ADDRINT > KnobEndHeapSegAddr(KNOB_MODE_WRITEONCE, "pintool", "end_heap_addr", "0x0", "specify end address of heap segment");
KNOB< ADDRINT > KnobStartStackSegAddr(KNOB_MODE_WRITEONCE, "pintool", "start_stack_addr", "0x0", "specify start address of stack segment");
KNOB< ADDRINT > KnobEndStackSegAddr(KNOB_MODE_WRITEONCE, "pintool", "end_stack_addr", "0x0", "specify end address of stack segment");

KNOB< string > KnobLoopName(KNOB_MODE_WRITEONCE, "pintool", "loop_name", "loop", "specify loop function name to be analyzed");
KNOB< string > KnobCallGraphPath(KNOB_MODE_WRITEONCE, "pintool", "path_to_callgraph", "./LoopExtractor_data/callgraphResult.extr", "specify path to the report from callgraph analysis");


//KNOB< BOOL > KnobPrintArgs(KNOB_MODE_WRITEONCE, "pintool", "a", "0", "print call arguments ");
//KNOB<BOOL>   KnobPrintArgs(KNOB_MODE_WRITEONCE, "pintool", "i", "0", "mark indirect calls ");

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
INT32 Usage() {
    cerr << "This tool produces a call trace." << endl << endl;
    cerr << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}
/* ===================================================================== */
string invalid = "invalid_rtn"; //assisting variable for Target2String
const string* Target2String(ADDRINT target) {
    string name = RTN_FindNameByAddress(target);
    if (name == "")
        return &invalid;
    else
        return new string(name);
}
/* ===================================================================== */
VOID LevelInc() {
	level++;
}
/* ===================================================================== */
VOID LevelDec() {
	level--;
}
VOID InstanceInc() {
	instance_id ++;
}
/* ===================================================================== */
VOID MemAccess(ADDRINT addr, ADDRINT addr_end) {
	//cerr << "Level: " << level << endl;
	//cerr << hex << addr << dec << endl;
	addrset.insert(addr);
	counting++;
	bool captured = false;
	if(startDataSegAddr <= addr && addr_end <= endDataSegAddr) {
		minDataSegAddr = std::min(minDataSegAddr, addr);
		maxDataSegAddr = std::max(maxDataSegAddr, addr_end);
		captured = true;
	}
	if(startHeapSegAddr <= addr && addr_end <= endHeapSegAddr) {
		minHeapSegAddr = std::min(minHeapSegAddr, addr);
		maxHeapSegAddr = std::max(maxHeapSegAddr, addr_end);
		captured = true;
	}
	/* For stack address, allow going pass current stack frame to callers */
	if(startStackSegAddr <= addr ) {
		minStackSegAddr = std::min(minStackSegAddr, addr);
		maxStackSegAddr = std::max(maxStackSegAddr, addr_end);
		captured = true;
	}
	if(!captured) {
		escaped_access_count++;
		escape_addrset.insert(addr);
	}
}
/* ===================================================================== */
VOID MemReads(ADDRINT addr, UINT32 size, ADDRINT inst) {
	if(level > 0 && instance_id == 1) MemAccess(addr, addr+size-1);
}
/* ===================================================================== */
VOID MemWrites(ADDRINT addr, UINT32 size, ADDRINT inst) {
	if(level > 0 && instance_id == 1) MemAccess(addr, addr+size-1);
}
/* ===================================================================== */
VOID ImageLoad(IMG img, VOID* v) {
	cerr << "Receiving rtn names from a file \n";
/*
	FILE* fp = fopen(callGraphFileName, "r");
	//Do fscanf here and insert each string into funcNames
	//char buf[100];
	std::string buf;
	while(fscanf(fp, "%s", buf) != EOF) {
		funcNames.insert(buf);
	}
	fclose(fp);
*/
	std::string line;
	std::ifstream input(callGraphFileName.c_str());
	//input.open(callGraphFileName);//, std::ios::in);
	while (std::getline(input, line))
	{
		RTN rtn = RTN_FindByName(img, line.c_str());
		if (RTN_Valid(rtn)) {
			ADDRINT rtnAddr = RTN_Address(rtn);
			funcNames.insert(line); //@@@ SHOULD be ADDRESS of a target function, not its name
			funcAddresses.insert(rtnAddr);
			cerr << "Function name: " << line << " ; Function address: " << hex << rtnAddr << dec << endl;
		}
	}
	input.close();
	/*
	cerr << "Generating a set of function names\n";
	//Collecting a set of function names and function addresses in current image
	for(SEC sec = IMG_SecHead(img); SEC_Valid(sec); sec = SEC_Next(sec)) {
		//cerr << "Analyzing Section " << SEC_Name(sec) << endl;
		for(RTN rtn = SEC_RtnHead(sec); RTN_Valid(rtn); rtn = RTN_Next(rtn)) {
			RTN_Open(rtn);
			for(INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {
				if(INS_IsCall(ins)) {
					//cerr << "Inserting a Func target\n";
					if(INS_IsDirectControlFlow(ins)) {
						ADDRINT target = INS_DirectControlFlowTargetAddress(ins);
						funcNames.insert(*(Target2String(target)));
						funcAddresses.insert(target);
					}
				}
			}
			RTN_Close(rtn);
		}
	}
	*/
	/*for(set<string>::iterator it = funcNames.begin(); it != funcNames.end(); it++) {
		cerr << "function name: " << *it << endl;
	}*/
	/*for(set<ADDRINT>::iterator it = funcAddresses.begin(); it != funcAddresses.end(); it++) {
		cerr << "function address: " << *it << endl;
	}*/

	//Inserting callbacks that will increment/decrement level
	//If level > 0, we're tracing memory accesses inside of functions from funcAddresses set
	//Otherwise, we skip the function
        RTN rtn = RTN_FindByName(img, loopFuncName.c_str());
        if(RTN_Valid(rtn)) {
		cerr << "Found loop in " << IMG_Name(img) << endl;
		cerr << "Loop name is " << loopFuncName << endl;
                RTN_Open(rtn);
		INS headIns = RTN_InsHead(rtn);
		INS tailIns = RTN_InsTail(rtn);
		cerr << "Head instruction: " << INS_Disassemble(headIns) << endl;
		cerr << "Tail instruction: " << INS_Disassemble(tailIns) << endl;
		INS_InsertCall(headIns, IPOINT_AFTER/*BEFORE*/, (AFUNPTR) LevelInc, IARG_END);
		INS_InsertCall(headIns, IPOINT_AFTER/*BEFORE*/, (AFUNPTR) InstanceInc, IARG_END);
		INS_InsertCall(tailIns, IPOINT_BEFORE/*AFTER*/,  (AFUNPTR) LevelDec, IARG_END);
			for(INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {
				if(INS_IsRet(ins)) {
					continue;  // skip ret instruction
				}
				if(INS_IsMemoryRead(ins)) {
					INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemReads, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_INST_PTR, IARG_END);
				}
				if(INS_IsMemoryWrite(ins)) {
					INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemWrites, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_INST_PTR, IARG_END);
				}
			}
                RTN_Close(rtn);
        } else {
                //cerr << "Can't find loop function"  <<endl;
        }

	//Inserting callbacks that will track memory addresses inside each RTN from funcAddresses set
	//ONLY if level > 0
	for(set<ADDRINT>::iterator it = funcAddresses.begin(); it != funcAddresses.end(); it++) {
		//cerr << "function address: " << *it << endl;
		RTN rtn = RTN_FindByAddress(*it);
		if(RTN_Valid(rtn)) {
			RTN_Open(rtn);
			for(INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {
				if(INS_IsRet(ins)) {
					continue;  // skip ret instruction
				}
				if(INS_IsMemoryRead(ins)) {
					INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemReads, IARG_MEMORYREAD_EA, IARG_MEMORYREAD_SIZE, IARG_INST_PTR, IARG_END);
				}
				if(INS_IsMemoryWrite(ins)) {
					INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemWrites, IARG_MEMORYWRITE_EA, IARG_MEMORYWRITE_SIZE, IARG_INST_PTR, IARG_END);
				}
			}
			RTN_Close(rtn);
		}
	}
}
/* ===================================================================== */
VOID PrintAddresses(string name, ADDRINT min_addr, ADDRINT max_addr) {
        //cerr << "min_addr: " << std::hex << min_addr << endl;
        //cerr << "max_addr: " << std::hex << max_addr << endl;
	ADDRINT print_min_addr = min_addr <= max_addr ? min_addr : 0;
	ADDRINT print_max_addr = min_addr <= max_addr ? max_addr : 0;
	
	*TraceFile << "Minimal " << name << " segment address: " << std::hex << print_min_addr << endl;
    *TraceFile << "Maximal " << name << " segment address: " << std::hex << print_max_addr << endl;

	*out << "Minimal " << name << " segment address: " << std::hex << print_min_addr << endl;
	*out << "Maximal " << name << " segment address: " << std::hex << print_max_addr << endl;
}
/* ===================================================================== */
VOID Fini(INT32 code, VOID* v)
{
	*out << "===============================================" << endl;
	*out << "HuskyTool analysis results: " << endl;
	//*out << "Minimal address: " << std::hex << minAddr << endl;
	//*out << "Maximal address: " << std::hex << maxAddr << endl;

	PrintAddresses("heap", minHeapSegAddr, maxHeapSegAddr);
	PrintAddresses("data", minDataSegAddr, maxDataSegAddr);
	PrintAddresses("stack", minStackSegAddr, maxStackSegAddr);
	*out << "address set size: " << std::dec << addrset.size() << endl;
	*out << "accesses count: " << std::dec << counting << endl;
	*out << "escaped accesses count: " << std::dec << escaped_access_count << endl;

	/*
	std::set<ADDRINT>::iterator it;
	*out << "all accesses:" << endl;
	for (it=addrset.begin(); it!=addrset.end(); ++it)
		*out << ' ' <<std::hex<< *it;
	*out << endl << "all escaped accesses:" << endl;
	for (it=escape_addrset.begin(); it!=escape_addrset.end(); ++it)
		*out << ' ' <<std::hex<< *it;
	*out << endl;
	*/

	*out << "===============================================" << endl;
}
/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
int main(int argc, char* argv[]) {
	PIN_InitSymbols();
	if (PIN_Init(argc, argv)) {
		return Usage();
	}

	string fileName = KnobOutputFile.Value();    

	startDataSegAddr = KnobStartDataSegAddr.Value();
	endDataSegAddr = KnobEndDataSegAddr.Value();
	minDataSegAddr = endDataSegAddr;
	maxDataSegAddr = startDataSegAddr;

	startHeapSegAddr = KnobStartHeapSegAddr.Value();
	endHeapSegAddr = KnobEndHeapSegAddr.Value();
	minHeapSegAddr = endHeapSegAddr;
	maxHeapSegAddr = startHeapSegAddr;

	startStackSegAddr = KnobStartStackSegAddr.Value();
	endStackSegAddr = KnobEndStackSegAddr.Value();
	minStackSegAddr = endStackSegAddr;
	maxStackSegAddr = startStackSegAddr;

	loopFuncName = KnobLoopName.Value();
	callGraphFileName = KnobCallGraphPath.Value();
	cerr << "callGraphFileName: " << callGraphFileName << endl;

	
    TraceFile = new std::ofstream("/tmp/out.trace.txt");

	if(!fileName.empty()) {
		out = new std::ofstream(fileName.c_str());
	}

	if(KnobCount) {
		IMG_AddInstrumentFunction(ImageLoad, 0);
		PIN_AddFiniFunction(Fini, 0);
	}

	cerr << "===============================================" << endl;
	cerr << "This application is instrumented by HuskyTool" << endl;
	if(!KnobOutputFile.Value().empty()) {
		cerr << "See file " << KnobOutputFile.Value() << " for analysis results" << endl;
	}
	cerr << "===============================================" << endl;


    // Never returns

	PIN_StartProgram();

	return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
