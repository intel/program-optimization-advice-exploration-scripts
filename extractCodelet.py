import os
from glob import glob
import json
import pandas as pd
import shutil
import subprocess
from subprocess import Popen, PIPE
from openpyxl import Workbook
from openpyxl import load_workbook
from operator import attrgetter
import csv
import re
import datetime
from Cheetah.Template import Template

SCRIPT_DIR=os.path.dirname(__file__)

# OneView paths
#prefix = "/host/localdisk/cwong29/working/codelet_extractor_work"
prefix = "/localdisk/cwong29/working/codelet_extractor_work"

#pathToCodeletExtractorDir = "/host/localdisk/spyankov/codelet-extractor"
pathToCodeletExtractorDir = f"{prefix}/codelet-extractor"
maqaoPath = f'{prefix}/cape-experiment-scripts/utils/MAQAO/maqao_new_2020'

# CloverLeaf paths
# BIN_NAME="MYCLOVER"
# BIN_NAME="clover_leaf"
# pathToAnalyzedBinary = f"{prefix}/CloverLeaf/{BIN_NAME}"
pathToBenchmark = f"{prefix}/CloverLeaf"

# LOOPFILEPATH = ""
# LOOPFILENAME = ""
# BASEFILENAME = ""
# LOOPOBJNAME = ""
# OBJDIR = "./obj" #pathToBenchmark + "/obj"
# MPIOBJDIR = "./mpiobj" #pathToBenchmark + "/mpiobj"
#PATHTOPIN = "/host/localdisk/spyankov/pin-3.22-98547-g7a303a835-gcc-linux"
PATHTOPIN = f"{prefix}/pin"
# compilerFlags="-std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data"

# Global variables for segment boundaries and min/max accessed memory addresses
class SegmentInfo:
    def __init__(self, tracer_data_dir):
        self.start_ds_addr = 0
        self.end_ds_addr = 0
        self.start_heap_addr = 0
        self.end_heap_addr = 0
        self.start_stack_addr = 0
        self.end_stack_addr = 0
        self.ds_min_addr = 0
        self.ds_max_addr = 0
        self.heap_min_addr = 0
        self.heap_max_addr = 0
        self.stack_min_addr = 0
        self.stack_max_addr = 0
        self.tracer_data_dir = tracer_data_dir
        self.tracer_out_txt_file = os.path.join(self.tracer_data_dir, 'out.txt')
        self.tracer_out_trace_txt_file = os.path.join(self.tracer_data_dir, 'out.trace.txt')
        self.tracer_out_addresses_h_file = os.path.join(self.tracer_data_dir, 'addresses.h')

    def run_trace(self, full_trace_binary, run_dir, loop_name, app_flags):
        self.runPin(full_trace_binary, app_flags, run_dir, loop_name, save_out_txt=True, move_out_trace_txt=False, verbose=True)
        self.getSegmentVars()
        self.runPin(full_trace_binary, app_flags, run_dir, loop_name, save_out_txt=False, move_out_trace_txt=True, verbose=True)
        self.getMinMaxVars()

    def run_save(self, full_save_binary, run_dir, loop_name, app_flags):
        self.runPin(full_save_binary, app_flags, run_dir, loop_name, save_out_txt=False, move_out_trace_txt=False, verbose=True)

    def runPin(self, binary, app_flags, run_dir, loop_name, save_out_txt, move_out_trace_txt, verbose=False):
        # Need to ensure directory exist or program will crash
        ensure_dir_exists(run_dir, 'myDataFile')
        myCmd = PATHTOPIN
        myCmd += "/pin -t "
        myCmd += PATHTOPIN
        #This line is used for more modern pintool (HuskyFuncTrace)
        myCmd += "/source/tools/HuskyFuncTrace/obj-intel64/HuskyFuncTrace.so -start_ds_addr " 
        #myCmd += "/source/tools/HuskyTool/obj-intel64/HuskyTool.so -start_ds_addr "
        myCmd += str(self.start_ds_addr)
        myCmd += " -end_ds_addr "
        myCmd += str(self.end_ds_addr)
        myCmd += " -start_heap_addr "
        myCmd += str(self.start_heap_addr)
        myCmd += " -end_heap_addr "
        myCmd += str(self.end_heap_addr)
        myCmd += " -start_stack_addr "
        myCmd += str(self.start_stack_addr)
        myCmd += " -end_stack_addr "
        myCmd += str(self.end_stack_addr)
        myCmd += " -loop_name "
        myCmd += loop_name
        #This line is used for more modern pintool (HuskyFuncTrace)
        #myCmd += " -path_to_callgraph ./LoopExtractor_data/callgraphResult.extr -- ./clover_leaf |& tee /tmp/out.txt" 
        #myCmd += " -- ./clover_leaf >> /tmp/out.txt"
        myCmd += f" -- {binary}{app_flags}"
        if save_out_txt:
            myCmd += f" > {self.tracer_out_txt_file}"
        runCmd(myCmd, cwd=run_dir, verbose=verbose)
        if move_out_trace_txt:
            shutil.move("/tmp/out.trace.txt", self.tracer_out_trace_txt_file)

    # Parsing text file with collected boundaries of heap, stack, data segment
    def getSegmentVars(self):
        tmpOutFile = open(self.tracer_out_txt_file, "r")
        for line in tmpOutFile:
            if re.search("STACK BEGIN", line):
                var = (line.split(": "))[-1]
                self.start_stack_addr = "0x"+(var[:len(var)-1])
            elif re.search("STACK END", line):
                var = (line.split(": "))[-1]
                self.end_stack_addr = "0x"+(var[:len(var)-1])
            elif re.search("HEAP START", line):
                var = (line.split(": "))[-1]
                self.start_heap_addr = "0x"+(var[:len(var)-1])
            elif re.search("HEAP END", line):
                var = (line.split(": "))[-1]
                self.end_heap_addr = "0x"+(var[:len(var)-1])
            elif re.search("DS START", line):
                var = (line.split(": "))[-1]
                self.start_ds_addr = "0x"+(var[:len(var)-1])
            elif re.search("DS END", line):
                var = (line.split(": "))[-1]
                self.end_ds_addr = "0x"+(var[:len(var)-1])
        tmpOutFile.close()

    # Parsing text file with collected minimal and maximal ACCESSES addresses of heap, stack, data segment
    def getMinMaxVars(self):
        traceOutFile = open(self.tracer_out_trace_txt_file, "r")
        for line in traceOutFile:
            if re.search("Minimal stack segment address", line):
                var = (line.split(": "))[-1]
                self.stack_min_addr = "0x"+(var[:len(var)-1])
            elif re.search("Maximal stack segment address", line):
                var = (line.split(": "))[-1]
                self.stack_max_addr = "0x"+(var[:len(var)-1])
            elif re.search("Minimal heap segment address", line):
                var = (line.split(": "))[-1]
                self.heap_min_addr = "0x"+(var[:len(var)-1])
            elif re.search("Maximal heap segment address", line):
                var = (line.split(": "))[-1]
                self.heap_max_addr = "0x"+(var[:len(var)-1])
            elif re.search("Minimal data segment address", line):
                var = (line.split(": "))[-1]
                self.ds_min_addr = "0x"+(var[:len(var)-1])
            elif re.search("Maximal data segment address", line):
                var = (line.split(": "))[-1]
                self.ds_max_addr = "0x"+(var[:len(var)-1])
        traceOutFile.close()
        self.generate_address_h()

    def generate_address_h(self):
        addressFile = open(self.tracer_out_addresses_h_file, "w")
        minStackLine = "#define min_stack_address ((unsigned char *) "
        minStackLine += str(self.stack_min_addr)
        minStackLine += ")\n"
        maxStackLine = "#define max_stack_address ((unsigned char *) "
        maxStackLine += str(self.stack_max_addr)
        maxStackLine += ")\n"
        minHeapLine = "#define min_heap_address ((unsigned char *) "
        minHeapLine += str(self.heap_min_addr)
        minHeapLine += ")\n"
        maxHeapLine = "#define max_heap_address ((unsigned char *) "
        maxHeapLine += str(self.heap_max_addr)
        maxHeapLine += ")\n"
        minDsLine = "#define min_ds_address ((unsigned char *) "
        minDsLine += str(self.ds_min_addr)
        minDsLine += ")\n"
        maxDsLine = "#define max_ds_address ((unsigned char *) "
        maxDsLine += str(self.ds_max_addr)
        maxDsLine += ")\n"
        L = [minStackLine, maxStackLine, minHeapLine, maxHeapLine, minDsLine, maxDsLine]
        addressFile.writelines(L)
        addressFile.close()

# Debug prints knob
isDebug = False

##################################################################################################
## Utility functions that move files, create or remove directories, and run other commands in bash
def runCmd(myCmd, cwd, env=os.environ.copy(), verbose=False):
    subprocess.run(myCmd, shell=True, env=env, cwd=cwd, capture_output=not verbose)
    
def runBashCmd(myCmd):
    #os.system(myCmd)
    try:
        subprocess.check_call(myCmd,stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    except:
        if isDebug:
            print("Error while running the command {} ", myCmd)

def makeDatafileDir(): 
    myDataFileCmd = "mkdir myDataFile"
    runBashCmd(myDataFileCmd)
    
def makeExtrObjDir(): 
    extrObjDirCmd = "mkdir ExtractedLoop_objfiles"
    runBashCmd(extrObjDirCmd)

# def makeCodeletDir():
#     codeletDirCmd = "mkdir -p ./LoopExtractor_data/codelet_"
#     fileName = LOOPFILENAME.split('.')
#     codeletDirCmd += fileName[-2]
#     runBashCmd(codeletDirCmd)

def moveFile(filepath, dest):
    moveCmd = "mv " + filepath + " " + dest
    runBashCmd(moveCmd)

def removeLoopExtractorDir():
    rmCmd = "rm -r ./LoopExtractor_data"
    runBashCmd(rmCmd)

def removeDatafileDir():
    rmCmd = "rm -r ./myDataFile"
    runBashCmd(rmCmd)

def removeExtrObjDir():
    rmCmd = "rm -r ./ExtractedLoop_objfiles"
    runBashCmd(rmCmd)

# def removeLoopObjFile():
#     rmCmd = "rm -r "
#     rmCmd += OBJDIR
#     rmCmd += "/"
#     fileName = (LOOPFILEPATH.split('/'))[-1]
#     objName = LOOPOBJNAME#getObjName(fileName)
#     rmCmd += objName
#     runBashCmd(rmCmd)
#     rmMpiCmd = "rm -r "
#     rmMpiCmd += MPIOBJDIR
#     rmMpiCmd += "/"
#     rmMpiCmd += objName
#     runBashCmd(rmMpiCmd)

def removeTmpFiles():
    rmCmd = "rm /tmp/out.txt"
    runBashCmd(rmCmd)
    rmTraceCmd = "rm /tmp/out.trace.txt"
    runBashCmd(rmTraceCmd)

def createLoopExtrWorkingDirectory():
    myCmd = "mkdir ./LoopExtractor_data"
    runBashCmd(myCmd)

def turnOffAddressRandomization():
    myCmd = "echo 0 |sudo tee /proc/sys/kernel/randomize_va_space"
    runBashCmd(myCmd)
##################################################################################################

# # Build and run the binary return the measurement output file dumped by MAQAO run
# def run_and_measure():
#     runMeasMaqao='LD_LIBRARY_PATH={}/lib:$LD_LIBRARY_PATH {}/maqao'.format(maqaoPath, maqaoPath)
#     meaOutFile=os.path.join(maqaoPath, 'out.txt')
#     myCmd='{} oneview -create-report=qprof -of=xlsx -binary={} -run_directory="{}" |tee {}'.format(runMeasMaqao, pathToAnalyzedBinary, pathToBenchmark, meaOutFile)
#     # Uncomment to run real measurement
#     #runBashCmd(myCmd)
#     return meaOutFile

# Generate transformation files, also compute total time
def parseReport(maqaoOutfile):
    #dataPath = pathToBinary.rsplit('/', 1)
    #fullRunDir = dataPath[0]
    transformDir=os.path.join(pathToBenchmark, 'reports')
    if not os.path.exists(transformDir):
        os.makedirs(transformDir)
    
    loopsToExtract = []

    result_file=subprocess.check_output("grep GENERATED {} |grep -v _detailed |grep -v ANALYTIC |cut -f3 -d:".format(maqaoOutfile), shell=True).strip().decode()
    #print("result file: {}".format(result_file))
    wb=load_workbook(result_file)
    totalTime=0
    if 'QPROF_full' in wb:
        ws = wb['QPROF_full']
        rows = list(ws.rows)
        hdr = list(map(attrgetter('value'), rows[0]))
        rows = list(dict(zip(hdr, list(map(attrgetter('value'), row)))) for row in rows[1:])
        loopList = []
        for row in rows:
            loopinfo = row['codelet.name']
            loopExecTime = row['Time(Second)']
            has_all = all([char in loopinfo for char in (',',)])
            if not has_all:
                loopList.append([loopExecTime, loopinfo])

        loopList.sort(reverse=True)
        numOfLoops=min(25, len(loopList))
        #print('TOP'+str(numOfLoops)+':')
        for i in range(0,numOfLoops):
            substr = loopList[i][1]
            pos = substr.find("_") + 1
            substr = substr[pos:]
            secondPos = substr.find(":")
            loopsToExtract.append([substr[:secondPos],substr[(secondPos+1):]])
        #print(loopsToExtract)
    return loopsToExtract

# Parsing string and returning a pair of integer values out of it
# FOR EXAMPLE: string \'18-18\' is parsed into a pair of two integer values [16,20]
# Extending the range by 2 due to inaccuracy detection of a loop by OneView
def parseLineNumberString(lineNumbers):
    firstLineNum,secondLineNum = lineNumbers.split('-')
    #return [int(firstLineNum)-2,int(secondLineNum)+2]
    return [int(firstLineNum)+3,int(secondLineNum)+10]

# Function that finds a full path to the loop file
# Currently, not working (returning the hardcoded global variable)
# def findLoopPath(loop):
#     pairOfNumbers = parseLineNumberString(loop[1])
#     myCmd = "cd "+pathToBenchmark
#     #os.system(myCmd)
#     subprocess.check_call(myCmd,stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
#     wd = os.getcwd()
#     os.chdir(pathToBenchmark)
#     loopPath=subprocess.check_output("pwd").strip().decode()#"find ./ -name \""+loop[0]+"\"").strip().decode() #.strip().decode()
#     os.chdir(wd)
#     #print("Found a filename: "+loopPath)
#     return LOOPFILEPATH

# Function that writes a csv file with a path to loopfile and loop line numbers
# This loop location file will be read in Rose tool to choose the loop to be extracted
def generateLoopLocFile(loopPath, begin_line, end_line, outdir="."):
    #pairOfNumbers = parseLineNumberString(lineNumbers)
    #begin_line = pairOfNumbers[0]
    #end_line = pairOfNumbers[1]
    row = [loopPath, begin_line, end_line]
    csvFileName = "tmpLoop.csv"
    with open(os.path.join(outdir, csvFileName), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)
    #return ('./'+csvFileName)

# Running Rose tool that does in-situ extraction and generate all necessary source files for in-vitro extraction
### THIS WORKS ONLY FOR CLOVERLEAF
# def extractLoop():
#     myCmd = pathToCodeletExtractorDir
#     myCmd += "/bin/LoopExtractor -I/usr/lib/x86_64-linux-gnu/openmpi/include -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -DUSE_OPENMP -lm "
#     myCmd += LOOPFILEPATH
#     runBashCmd(myCmd)

# def build(ver, main_cc_file="./src/clover_leaf.cc"):
#     #myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/codelet_"
#     outdir=f"./ExtractedLoop_objfiles/{ver}"
#     outobj=os.path.join(outdir, LOOPOBJNAME)
#     os.makedirs(outdir, exist_ok=True)

#     myCmd = f"mpic++ {compilerFlags} -c ./LoopExtractor_data/codelet_"
#     fileName = LOOPFILENAME.split('.')
#     myCmd += fileName[-2]
#     myCmd += f"/{ver}_"+BASEFILENAME
#     myCmd += f" -o {outobj}"
#     #myCmd += " -o ./ExtractedLoop_objfiles/"
#     #myCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1])
#     runBashCmd(myCmd)
#     #buildBinary(ver)
#     myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -fopenmp -DUSE_OPENMP "
#     myCmd += OBJDIR
#     myCmd += "/*.o " 
#     myCmd += MPIOBJDIR
#     myCmd += f"/*.o ./ExtractedLoop_objfiles/*.o {outobj} "
#     myCmd += f"{main_cc_file} -o "
#     myCmd += f"./{ver}"
#     runBashCmd(myCmd)

    


# Generation of an object file for some utilities necessary for running in-vitro extraction
### THIS WORKS FOR CLOVERLEAF OR OTHER BENCHMARKS THAT USE OBJECT FILES AS PART OF BUILDING PROCESS
def buildUtil():
    myCmd = "gcc -std=c++11 -c -o util.o -I. -I./LoopExtractor_data ./LoopExtractor_data/util.c"
    runBashCmd(myCmd)
    moveCmd = "mv util.o ./ExtractedLoop_objfiles"
    runBashCmd(moveCmd)

# Generating an object file of an extracted (in-situ) loop
# ### THIS WORKS ONLY FOR CLOVERLEAF
# def buildLoopFile():
#     myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/"
#     myCmd += LOOPFILENAME
#     myCmd += " -o ./ExtractedLoop_objfiles/"
#     myCmd += (LOOPFILENAME.split('.'))[-2]
#     myCmd += ".o"
#     runBashCmd(myCmd)
    
# Parsing string with a source file name so to generate object file name out of it (by replacing an extension)
### THIS WORKS FOR CLOVERLEAF OR OTHER BENCHMARKS THAT USE OBJECT FILES AS PART OF BUILDING PROCESS
def getObjName(sourceFileName):
    fileName = sourceFileName.split('.')
    objFileName = fileName[-2] + ".o"
    return objFileName

# # Function that receives loop file names that were generated during the execution of Rose tool
# def getLoopFileNames():
#     with open('/tmp/loopFileNames.txt') as loopFileNames: 
#         lines = loopFileNames.readlines()
#         baseStr = lines[0]
#         loopStr = lines[1]
#         global BASEFILENAME
#         BASEFILENAME = baseStr[:len(baseStr)-1]
#         global LOOPFILENAME
#         LOOPFILENAME = loopStr[:len(loopStr)-1]
#         global LOOPOBJNAME
#         LOOPOBJNAME = getObjName((LOOPFILEPATH.split('/'))[-1])

def getLoopFileNames1(loop_name_file):
    with open(loop_name_file) as loopFileNames: 
        lines = loopFileNames.readlines()
        baseStr = lines[0]
        loopStr = lines[1]
        restoreStr = lines[2]
    return baseStr.strip(), loopStr.strip(), restoreStr.strip()

# Generation of a binary out of previously generated object files
### THIS WORKS ONLY FOR CLOVERLEAF
# def buildBinary(binary):
#     myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -fopenmp -DUSE_OPENMP "
#     myCmd += OBJDIR
#     myCmd += "/*.o " 
#     myCmd += MPIOBJDIR
#     myCmd += "/*.o ./ExtractedLoop_objfiles/*.o "
#     myCmd += "./src/clover_leaf.cc -o "
#     myCmd += f"./{binary}"
#     runBashCmd(myCmd)

# Building a benchmark where base file was replaced with TRACE source file
# to trace memory access addresses
### THIS WORKS ONLY FOR CLOVERLEAF
# def buildTraceSourceFile():
#     build("trace")
    # myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/codelet_"
    # fileName = LOOPFILENAME.split('.')
    # myCmd += fileName[-2]
    # myCmd += "/trace_"+BASEFILENAME
    # myCmd += " -o ./ExtractedLoop_objfiles/"
    # myCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1]))
    # runBashCmd(myCmd)
    # buildBinary("trace")

# Running pintool to trace/save memory addresses
### THIS WORKS ONLY FOR CLOVERLEAF
# def runPin(passNum, binary):
#     myCmd = PATHTOPIN
#     myCmd += "/pin -t "
#     myCmd += PATHTOPIN
#     #This line is used for more modern pintool (HuskyFuncTrace)
#     myCmd += "/source/tools/HuskyFuncTrace/obj-intel64/HuskyFuncTrace.so -start_ds_addr " 
#     #myCmd += "/source/tools/HuskyTool/obj-intel64/HuskyTool.so -start_ds_addr "
#     myCmd += str(start_ds_addr)
#     myCmd += " -end_ds_addr "
#     myCmd += str(end_ds_addr)
#     myCmd += " -start_heap_addr "
#     myCmd += str(start_heap_addr)
#     myCmd += " -end_heap_addr "
#     myCmd += str(end_heap_addr)
#     myCmd += " -start_stack_addr "
#     myCmd += str(start_stack_addr)
#     myCmd += " -end_stack_addr "
#     myCmd += str(end_stack_addr)
#     myCmd += " -loop_name "
#     fileName = LOOPFILENAME.split('.')
#     myCmd += fileName[-2]
#     #This line is used for more modern pintool (HuskyFuncTrace)
#     #myCmd += " -path_to_callgraph ./LoopExtractor_data/callgraphResult.extr -- ./clover_leaf |& tee /tmp/out.txt" 
#     if passNum == 0:
#         #myCmd += " -- ./clover_leaf >> /tmp/out.txt"
#         myCmd += f" -- ./{binary} >> /tmp/out.txt"
#     elif passNum == 1:
#         #myCmd += " -- ./clover_leaf "# >> /tmp/out.trace.txt"
#         myCmd += f" -- ./{binary} "# >> /tmp/out.trace.txt"
#     runBashCmd(myCmd)




# Running TRACE inside of a pintool
# First pass collects segment boundaries (minimal and maximal addresses stack, heap, data segment)
# Second pass traces minimal and maximal ACCESSES addresses of stack, heap, data segment
# def runTrace():
#     removeTmpFiles()
#     # First pass
#     runPin(0, 'trace')
#     getSegmentVars()
#     # Second pass
#     runPin(1, 'trace')
#     getMinMaxVars()

# Copying util files necessary for running in-vitro extraction
def copyUtilFiles():
    utilCmd = "cp "
    utilCmd += pathToCodeletExtractorDir
    utilCmd += "/src/tracer/util.* ./LoopExtractor_data"
    runBashCmd(utilCmd)
    defsCmd = "cp "
    defsCmd += pathToCodeletExtractorDir
    defsCmd += "/src/tracer/defs.h ./LoopExtractor_data"
    runBashCmd(defsCmd)

# Building a benchmark where base file was replaced with SAVE source file
# to save data from traced memory access addresses
### THIS WORKS ONLY FOR CLOVERLEAF
# def buildSaveSourceFile():
#     build("save")
    # myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/codelet_"
    # fileName = LOOPFILENAME.split('.')
    # myCmd += fileName[-2]
    # myCmd += "/save_"+BASEFILENAME
    # myCmd += " -o ./ExtractedLoop_objfiles/"
    # myCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1])
    # runBashCmd(myCmd)
    # buildBinary("save")

# Building a driver file from RESTORE source file and generate a binary of a codelet
### THIS WORKS ONLY FOR CLOVERLEAF
# def buildRestoreSourceFile():
#     ver="restore"
#     outdir=f"./ExtractedLoop_objfiles/{ver}"
#     outobj=os.path.join(outdir, LOOPOBJNAME)
#     os.makedirs(outdir, exist_ok=True)
#     #myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -fopenmp -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data "
#     myCmd = f"mpic++ {compilerFlags} -c ./LoopExtractor_data/codelet_"
#     fileName = LOOPFILENAME.split('.')
#     myCmd += fileName[-2]
#     myCmd += f"/{ver}_" + BASEFILENAME
#     myCmd += f" -o {outobj}"
#     #myCmd += " -o ./ExtractedLoop_objfiles/"
#     #myCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1])
#     runBashCmd(myCmd)
    
#     myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -fopenmp -DUSE_OPENMP "
#     myCmd += OBJDIR
#     myCmd += "/*.o " 
#     myCmd += MPIOBJDIR
#     myCmd += f"/*.o ./ExtractedLoop_objfiles/*.o {outobj} "
#     #myCmd += "./src/clover_leaf_no_main.cc -o "
#     myCmd += " -o "
#     myCmd += f"./{ver}"
#     runBashCmd(myCmd)


# Running SAVE inside of a pintool
# def runSave():
#     runPin(1, 'save')

# # Building TRACE, SAVE, and RESTORE source files and running them to save datafiles
# def generateCodelet():
#     copyUtilFiles()
#     getLoopFileNames()
#     makeCodeletDir()
#     buildUtil()
#     buildLoopFile()
#     removeLoopObjFile()
#     buildTraceSourceFile()
#     print("Tracing memory addresses")
#     runTrace()
#     print("FINISHED tracing memory addresses!")
#     buildSaveSourceFile()
#     print("Saving data from traced memory addresses")
#     runSave() 
#     print("FINISHED saving the data")
#     buildBenchmark()
#     rmCmd = "rm ./ExtractedLoop_objfiles/"
#     rmCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1])
#     runBashCmd(rmCmd)
#     build("restore", "./src/clover_leaf_no_main.cc")
#     #buildRestoreSourceFile()

# Building the benchmark from scratch
### THIS WORKS ONLY FOR CLOVERLEAF
def buildBenchmark():
    myCmd = "make clean\nmake COMPILER=GNU USE_OPENMP=1\n"
    runBashCmd(myCmd)

# Generate config.h header file and write instance number 0 there
# Instance number is used during In-Vitro extraction to choose which execution instance of the loop to save (and restore as a codelet)
def initiateConfig(instanceNum):
    configFile = open('lore_config.h', 'w')
    instLine = "extern int extr_instance;\n"
    configFile.write(instLine)
    configFile.close()
    myCmd = "mv config.h ./LoopExtractor_data"
    runBashCmd(myCmd)

def initiateConfig1(outdir, instanceNum=0):
    configFile = open(os.path.join(outdir, 'lore_config.h'), 'w')
    #instLine = f"extern int extr_instance = {instanceNum};\n"
    instLine = f"extern int extr_instance;\n"
    configFile.write(instLine)
    configFile.close()

# Function responsible for the extraction process
### THIS WORKS FOR SPECIFIC SOURCE FILES FROM CLOVERLEAF
# def runExtractor(loopsToExtract):
#     # Creating Loop Extractor working directory
#     createLoopExtrWorkingDirectory()
#     initiateConfig(0)
#     # Currently running it on a specific example, ignoring the parameter loopsToExtract
#     # When parsing of OneView report will be finished, replace the lines of code above with a commented loop
#     #loop = ["update_halo.cc","37-37"]
#     loop = ["clover.cc","81-81"]
#     global LOOPFILEPATH
#     #LOOPFILEPATH = "/host/localdisk/spyankov/CloverLeaf/src/update_halo.cc"
#     #LOOPFILEPATH = "/host/localdisk/spyankov/CloverLeaf/src/clover.cc"
#     LOOPFILEPATH = f"{prefix}/CloverLeaf/src/clover.cc"
#     loopPath = findLoopPath(loop) #NOT WORKING AT THE MOMENT, RETURNING THE LOOPFILEPATH GLOBAL VARIABLE
#     # Generating a Loop Location file with info about a loop (path to a file and line number of a loop) 
#     # that should be extracted to the working directory
#     loopLocFilePath = generateLoopLocFile(loopPath, loop[1])
#     moveFile(loopLocFilePath, "./LoopExtractor_data")
#     # Running Rose tool
#     extractLoop()
#     # Saving data and build all necessary source files to generate a codelet  
#     generateCodelet()

#    for loop in loopsToExtract:
#        loopPath = findLoopPath(loop)
#        loopLocFilePath = generateLoopLocFile(loopPath, loop[1])
#        moveFile(loopLocFilePath, "./LoopExtractor_data")
#        extractLoop()
#        generateCodelet()

# Function that run all necessary commands to prepare the environment for the extraction process
def prepareForExtraction():
    turnOffAddressRandomization()
    # After the next line all work will be in the benchmark directory
    os.chdir(pathToBenchmark)
    removeLoopExtractorDir()
    removeDatafileDir()
    removeExtrObjDir()
    removeTmpFiles()
    makeDatafileDir()
    makeExtrObjDir()
    buildBenchmark()

# # Function that runs OneView and Chooses loops that should be extracted by parsing OneView report
# def runOneView():
#     pathToReport = run_and_measure()
#     loopsToExtract = parseReport(pathToReport)
#     return loopsToExtract

def load_advisor_env():
    script = '/host/opt/intel/oneapi/advisor/2023.0.0/advisor-vars.sh'
    #script = os.path.join(compiler_dir, 'Linux/intel64/load.sh')
    #script = '/nfs/site/proj/openmp/compilers/intel/19.0/Linux/intel64/load.sh'
    pipe = subprocess.Popen(f"/bin/bash -c 'source {script} --force && env'", stdout=subprocess.PIPE, shell=True)
    output = pipe.communicate()[0]
    #for line in output.splitlines():
    #    print(str(line).split("=", 1))
    env = dict((line.split("=", 1) if '=' in line else ('','') for line in output.decode('utf-8').splitlines()))
    # try to pop the dummy '' key
    env.pop('','')
    return env

def generate_timestamp_str():
    return timestamp_str(generate_timestamp())

def generate_timestamp():
    return int(round(datetime.datetime.now().timestamp()))

def timestamp_str(timestamp):
    ts_str = str(timestamp)
    ts_str = ts_str[:3] + "-" + ts_str[3:6] + "-" + ts_str[6:]
    return ts_str




def main():
    ## PREPARE
    clean = True
    build_app=True

    loop_extractor_path=os.path.join(prefix, "codelet-extractor/bin/LoopExtractor")


    binary='clover_leaf'
    cmakelist_dir=os.path.join(prefix,'CloverLeaf_cmake')
    
    cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-DUSE_OPENMP"'
    cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-DUSE_OPENMP -g" -DCMAKE_C_FLAGS="-g"'
    cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-cxx=icpx -DUSE_OPENMP -g" -DCMAKE_C_FLAGS="-g"'

    app_data_file = os.path.join(cmakelist_dir, 'clover.in')

    app_flags = ''
    

    if True:
        binary='525.x264_r'
        cmakelist_dir=os.path.join(prefix, 'SPEC2017/llvm-test-suite')
        src_dir=os.path.join(prefix, 'SPEC2017/benchmark')
        cmake_flags = f'-DTEST_SUITE_SUBDIRS=External/SPEC/CINT2017rate -DTEST_SUITE_SPEC2017_ROOT={src_dir} -DCMAKE_C_COMPILER=icx -DTEST_SUITE_COLLECT_CODE_SIZE=OFF'
        cmake_flags = f'-DTEST_SUITE_SUBDIRS=External/SPEC/CINT2017rate -DTEST_SUITE_SPEC2017_ROOT={src_dir} -DCMAKE_C_COMPILER=icx -DCMAKE_C_FLAGS="-g -DSPEC" -DCMAKE_CXX_FLAGS="-g -DSPEC" -DTEST_SUITE_COLLECT_CODE_SIZE=OFF'
        #cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-g" -DCMAKE_CXX_FLAGS="-DUSE_OPENMP"'
        #cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g"'

        app_data_file=os.path.join(prefix, 'SPEC2017/benchmark/benchspec/CPU/525.x264_r/run/run_base_test_myTest.0000/BuckBunny.yuv')

        app_flags = ' --dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720'


    #src_dir='/localdisk/cwong29/working/codelet_extractor_work/SPEC2017'
    #build_dir=f'{src_dir}-build'
    timestamp_str = generate_timestamp_str()

    run_cmake_dir=os.path.abspath(os.path.join(cmakelist_dir, '..'))
    extractor_work_dir=os.path.join(run_cmake_dir, 'extractor_work')
    extractor_work_dir=os.path.join(extractor_work_dir, binary, timestamp_str)
    build_dir=os.path.join(extractor_work_dir, 'build')

    if clean:
        shutil.rmtree(extractor_work_dir, ignore_errors=True)
    os.makedirs(extractor_work_dir, exist_ok=True)

    loop_extractor_data_dir = ensure_dir_exists(extractor_work_dir, 'LoopExtractor_data')

    # Build app
    # Change original CMakeLists.txt to include extractor code building script if not done before

    if build_app:
        shutil.rmtree(build_dir, ignore_errors=True)
        #run_cmake3(binary, src_dir, build_dir, run_cmake_dir, cmake_flags) 
        run_cmake(cmakelist_dir, build_dir, run_cmake_dir, cmake_flags, binary)


    profile_data_dir = ensure_dir_exists(extractor_work_dir, 'profile_data')
    for r, d, fs in os.walk(build_dir):
        if binary in fs:
            full_binary_path=os.path.join(r, binary)
            break
    #full_binary_path = os.path.join(build_dir, binary)
    #shutil.copy2(full_binary_path, profile_data_dir)
    os.symlink(full_binary_path, os.path.join(profile_data_dir, os.path.basename(full_binary_path)))
    link_app_data_file(profile_data_dir, app_data_file)
    #shutil.copy2(app_data_file, profile_data_dir)


    adv_proj_dir = os.path.join(profile_data_dir, f'proj_{timestamp_str}')

    adv_env = load_advisor_env()
    #app_cmd = f'./{binary}'
    app_cmd = f'./{binary}{app_flags}'
    if True:
        runCmd(f'advixe-cl --collect survey --project-dir {adv_proj_dir} -- {app_cmd}', 
           cwd=profile_data_dir, env=adv_env, verbose=True)

        profile_csv = os.path.join(profile_data_dir, 'profile.csv')
        runCmd(f'advisor --report joined --project-dir={adv_proj_dir} > {profile_csv}',
           cwd=profile_data_dir, env=adv_env, verbose=True)
    profile_df = pd.read_csv(profile_csv, skiprows=1, delimiter=',')
    #profile_df = pd.read_csv('/tmp/profile.csv', skiprows=1, delimiter=',')
    #profile_df = pd.read_csv('/tmp/profile-525.csv', skiprows=1, delimiter=',')
    #profile_df = pd.read_csv('/tmp/profile-clover.csv', skiprows=1, delimiter=',')
    # Select loops only
    loop_profile_df = profile_df[profile_df['function_instance_type'] == 2]
    loop_profile_df = loop_profile_df.sort_values(by='self_time', ascending=False)

    idx = 0
    idx = 21
    idx = 16


    n = 21
    n = 1
    for idx in range(0, n):
        extract_codelet(loop_extractor_path, binary, cmakelist_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, 
                        cmake_flags, loop_profile_df, idx, prefix, app_flags, app_data_file)
    print("DONE")

def link_app_data_file(profile_data_dir, app_data_file):
    os.symlink(app_data_file, os.path.join(profile_data_dir, os.path.basename(app_data_file)))


def extract_codelet(loop_extractor_path, binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, profile_df, 
                    idx, prefix, app_flags, app_data_file):
    top_row = profile_df.iloc[idx]
    full_source_path = top_row['source_full_path']
    source_location = top_row['source_location']
    compilation_flags = top_row['compilation_flags']
    source_line = int(top_row['line'])
    source_path = os.path.relpath(full_source_path, src_dir)

    #source_path = "src/clover.cc"
    #source_path = "src/adaptors/ideal_gas.cpp"
    #source_line = 43
    source_file = os.path.join(src_dir, source_path)


    source_file = full_source_path
    #source_file = os.path.join(src_dir, "src", "adaptors", "ideal_gas.cpp")
    src_folder=os.path.dirname(source_file)
    #loop = [ source_file ,81+3, 81+10]
    #loop = [ source_file ,43, 74]
    loop = [ source_file , source_line, source_line]

    
    
    compile_command_json_file = os.path.join(build_dir, 'compile_commands.json')
    with open(compile_command_json_file, 'r') as f:
        for compile_command in json.load(f):
            cnt_file = compile_command['file']
            print(cnt_file)
            if os.path.samefile(cnt_file, source_file):
                print('match')
                matched_command = compile_command['command']
                command_directory = compile_command['directory']
                print(matched_command)
                #inc_flags = [part for part in matched_command.split(" ") if part.startswith('-I')]+[f'-I{src_folder}']
                #non_inc_flags = [part for part in matched_command.split(" ") if not part.startswith('-I') and len(part)>0 ]
                command_parts = matched_command.split(" ")
                compiler = os.path.basename(command_parts[0])
                if compiler == "mpiicpc": 
                    # Intel MPI wrapper
                    # remove existing -cxx flags
                    command_parts = [x for x in command_parts if not x.startswith('-cxx=')]
                    command_parts.insert(1, f"-I{src_folder}")
                    command_parts.insert(1, f"-cxx={loop_extractor_path}")
                else:
                    # TODO: fix hardcoded
                    compiler_full_path = shutil.which("icx")
                    command_parts = [loop_extractor_path if x == compiler_full_path else x for x in command_parts]
                loop_extractor_command = " ".join(command_parts+['--extractwd', extractor_work_dir, '--extractsrcprefix', prefix])
                    
                if os.path.basename(compiler).startswith("mpi"):
                    # MPI compilers
                    pass 
                else:
                    pass


    # Extractor loop using in-situ extractor
    generateLoopLocFile(loop[0], loop[1], loop[2], loop_extractor_data_dir)
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH']+':/usr/lib/jvm/java-11-openjdk-amd64/lib/server'
    env['OMP_NUM_THREADS']="1"
    
    #runCmd(loop_extractor_command, cwd=extractor_work_dir, env=env, verbose=True)

    #data_dir_symlink = os.path.join(command_directory, os.path.basename(loop_extractor_data_dir))
    #if os.path.islink(data_dir_symlink):
    #    os.unlink(data_dir_symlink)
    #os.symlink(loop_extractor_data_dir, data_dir_symlink)
    runCmd(loop_extractor_command, cwd=command_directory, env=env, verbose=True)
    basefilename, loopfilename, restore_src_file = getLoopFileNames1('/tmp/loopFileNames.txt')

    name_map, loop_file, util_h_file, util_c_file, segment_info, save_data_dir, save_pointers_h_file = capture_data(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, app_flags, app_data_file, full_source_path, source_path, basefilename, loopfilename)
    
    restore_binary=f'restore_{binary}'
    restore_work_dir = ensure_dir_exists(extractor_work_dir, 'restore_data')
    extracted_codelet_dir = ensure_dir_exists(restore_work_dir, 'codelet')
    extracted_codelet_build_dir = ensure_dir_exists(restore_work_dir, 'codelet_build')

    restore_include_dir = ensure_dir_exists(extracted_codelet_dir, 'include')
    restore_src_dir = ensure_dir_exists(extracted_codelet_dir, 'src')
    shutil.copy2(util_c_file, restore_src_dir)

    loop_ext = os.path.splitext(loopfilename)[-1]
    #restore_src_file = "/tmp/restore.cc"
    driver_src_file = f'restore{loop_ext}'
    name_map['driver_src'] = driver_src_file
    shutil.copy2(restore_src_file, os.path.join(restore_src_dir, driver_src_file))
    shutil.copy2(loop_file, restore_src_dir)
    # defs.h needed by util.c
    defs_h_file = os.path.join(SCRIPT_DIR, 'src', 'tracer', 'defs.h')
    shutil.copy2(defs_h_file, restore_include_dir)
    shutil.copy2(util_h_file, restore_include_dir)
    shutil.copy2(save_pointers_h_file, restore_include_dir)
    shutil.copy2(segment_info.tracer_out_addresses_h_file, restore_include_dir)

    # Restore/extracted codelet CMakeLists.txt file generation.
    instantiate_cmakelists_file(name_map, in_template = 'CMakeLists.restore.template', 
                                out_instantiated_file=os.path.join(extracted_codelet_dir, 'CMakeLists.txt'))

    #shutil.copy2(extracted_cmakelist_txt_template_file, extracted_cmakelist_txt_file)

    restore_data_dir = ensure_dir_exists(extracted_codelet_dir, 'data')
    #shutil.copy2(save_data_dir, restore_data_dir)
    restore_my_datafile_dir = os.path.join(restore_data_dir, 'myDataFile')
    shutil.copytree(save_data_dir, restore_my_datafile_dir)



    # Try to build restore (extracted codelete)
    restore_cmake_flags = f'-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-g -D__RESTORE_CODELET__" -DCMAKE_C_FLAGS="-g -D__RESTORE_CODELET__"'
    #run_cmake2(restore_binary, restore_work_dir, extracted_codelet_dir, extracted_codelet_build_dir, restore_cmake_flags)
    run_cmake(extracted_codelet_dir, extracted_codelet_build_dir, restore_work_dir, restore_cmake_flags, restore_binary)

    restore_run_dir = ensure_dir_exists(restore_work_dir, 'run')
    shutil.copytree(restore_my_datafile_dir, os.path.join(restore_run_dir, 'myDataFile'))
    shutil.copy2(os.path.join(extracted_codelet_build_dir, restore_binary), restore_run_dir)
    # Now can run built extracted codelet
    runCmd(f'./{restore_binary}', cwd=restore_run_dir, verbose=True)

    #compilerflags=
    #runCmd(f"mpiicpc -c -cxx={loop_extractor_path} -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -DUSE_OPENMP -lm /host/localdisk/cwong29/working/codelet_extractor_work/CloverLeaf/src/clover.cc -o /tmp/test.o
    #", extractor_work_dir, verbose=True)
    return

def capture_data(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, app_flags, app_data_file, full_source_path, source_path, basefilename, loopfilename):
    cmake_extractor_src_dir = ensure_dir_exists(src_dir, 'extractor_src')
    cmake_extractor_include_dir = ensure_dir_exists(src_dir, 'extractor_include')


    name_map = { "loop_src" : loopfilename, "binary" : binary, 
                "base_src": basefilename, "orig_src_path": full_source_path, 
                "orig_src_folder": os.path.dirname(source_path)}
    update_app_cmakelists_file(src_dir, name_map)

    #trace_src_file = single_glob(f'{extractor_codelet_src_dir}/trace_*')
    trace_src_file = os.path.join(loop_extractor_data_dir, basefilename)
    shutil.copy2(trace_src_file, cmake_extractor_src_dir)

    loop_file = os.path.join(loop_extractor_data_dir, loopfilename)
    shutil.copy2(loop_file, cmake_extractor_src_dir)


    initiateConfig1(cmake_extractor_include_dir)
    util_h_file = os.path.join(SCRIPT_DIR, 'src', 'tracer', 'util.h')
    shutil.copy2(util_h_file, cmake_extractor_include_dir)
    util_c_file = os.path.join(SCRIPT_DIR, 'src', 'tracer', 'util.c')
    shutil.copy2(util_c_file, cmake_extractor_src_dir)
    

    tracer_dir = ensure_dir_exists(extractor_work_dir, 'tracer_data')
    tracer_run_dir = ensure_dir_exists(tracer_dir, 'run')
    link_app_data_file(tracer_run_dir, app_data_file)
    segment_info = SegmentInfo(tracer_dir)
    segment_info.generate_address_h()
    shutil.copy2(segment_info.tracer_out_addresses_h_file, cmake_extractor_include_dir)

    trace_binary=f'trace_{binary}'
    run_cmake(src_dir, build_dir, run_cmake_dir, f'-DBUILD_TRACE=ON {cmake_flags}', trace_binary)

    # Run at source directory for CloverLeaf but can be generalized as CLA
    fileName = loopfilename.split('.')
    loop_name = fileName[-2]

    #return

    print("Tracing memory addresses")
    segment_info.run_trace(os.path.join(build_dir, trace_binary), tracer_run_dir, loop_name, app_flags)
    print("FINISHED tracing memory addresses!")

    #save_src_file = single_glob(f'{extractor_codelet_src_dir}/save_*')
    #shutil.copy2(save_src_file, cmake_extractor_src_dir)
    #util_c_file = os.path.join(script_dir, 'src', 'tracer', 'util.c')
    #shutil.copy2(util_c_file, cmake_extractor_src_dir)
    #defs_h_file = os.path.join(script_dir, 'src', 'tracer', 'defs.h')
    #shutil.copy2(defs_h_file, cmake_extractor_include_dir)
    # Copy updated address.h file to include to rebuild to save right heap and stack data
    shutil.copy2(segment_info.tracer_out_addresses_h_file, cmake_extractor_include_dir)

    save_binary=f'save_{binary}'
    run_cmake(src_dir, build_dir, run_cmake_dir, f'-DBUILD_SAVE=ON {cmake_flags}', save_binary)

    save_work_dir = ensure_dir_exists(extractor_work_dir, 'save_data')
    save_run_dir = ensure_dir_exists(save_work_dir, 'run')
    link_app_data_file(save_run_dir, app_data_file)
    segment_info.run_save(os.path.join(build_dir, save_binary), save_run_dir, loop_name, app_flags)

    save_data_dir = ensure_dir_exists(save_run_dir, 'myDataFile')
    save_pointers_h_file = os.path.join(save_run_dir, 'saved_pointers.h')
    save_data_dir=shutil.move(save_data_dir, save_work_dir)
    save_pointers_h_file=shutil.move(save_pointers_h_file, save_work_dir)
    return name_map,loop_file,util_h_file,util_c_file,segment_info,save_data_dir,save_pointers_h_file

#def run_cmake3(binary, src_dir, build_dir, run_cmake_dir, cmake_flags):
# def run_cmake3(src_dir, build_dir, run_cmake_dir, cmake_flags, binary):
#     runCmd(f'cmake {cmake_flags} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -S {src_dir} -B {build_dir}', cwd=run_cmake_dir, verbose=True)
#     runCmd(f'cmake --build {build_dir} --target {binary}', cwd=run_cmake_dir, verbose=True)

# def run_cmake2(restore_binary, restore_work_dir, extracted_codelet_dir, extracted_codelet_build_dir, restore_cmake_flags):
# def run_cmake2(extracted_codelet_dir, extracted_codelet_build_dir, restore_work_dir, restore_cmake_flags, restore_binary):
#     runCmd(f'cmake {restore_cmake_flags} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -S {extracted_codelet_dir} -B {extracted_codelet_build_dir}', cwd=restore_work_dir, verbose=True)
#     runCmd(f'cmake --build {extracted_codelet_build_dir} --target {restore_binary}', cwd=restore_work_dir, verbose=True)

def run_cmake(cmakelist_dir, build_dir, run_cmake_dir, cmake_flags, trace_binary):
    runCmd(f'cmake {cmake_flags} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -S {cmakelist_dir} -B {build_dir}', cwd=run_cmake_dir, verbose=True)
    runCmd(f'cmake --build {build_dir} --target {trace_binary}', cwd=run_cmake_dir, verbose=True)

def update_app_cmakelists_file(src_dir, name_map):
    orig_cmakelist_txt_file = os.path.join(src_dir, 'CMakeLists.txt')
    extractor_build_file = 'CMakeLists.extractor.txt'
    include_extractor_build_line = f"include({extractor_build_file})"
    with open(orig_cmakelist_txt_file, 'r+') as file:
        for line in file:
            if include_extractor_build_line in line:
                break
        else:
            # The line to include extra build code is not in so add one
            file.write(include_extractor_build_line)

    instantiate_cmakelists_file(name_map, in_template = 'CMakeLists.extractor.template', 
                                out_instantiated_file=os.path.join(src_dir, extractor_build_file))

def instantiate_cmakelists_file(name_map, in_template, out_instantiated_file):
    extracted_cmakelist_txt_template_file=os.path.join(SCRIPT_DIR, 'templates', in_template)
    restore_cmakelist_txt_template = Template.compile(file=extracted_cmakelist_txt_template_file)
    #names = { "loop_src" : "clover_clover_exchange_line84_localdiskcwong29workingcodelet_extractor_workCloverLeaf_cmakesrc.cc" }
    restore_cmakelist_txt_def = restore_cmakelist_txt_template(searchList=[name_map])
    print(restore_cmakelist_txt_def, file=open(out_instantiated_file, 'w'))
    # print("Preparing the environment for the extraction")
    # prepareForExtraction()
    # print("FINISHED preparing the environment!")

    # ## ONEVIEW REPORT
    # print("Running OneView")
    # loopsToExtract = runOneView()
    # print("FINISHED running OneView!")

    # ## EXTRACTING A CODELET
    # print("Extracting a codelet")
    # runExtractor(loopsToExtract)
    # print("FINISHED the extraction of a codelet!")

def ensure_dir_exists(parent_dir, child_dir):
    trace_data_dir=os.path.join(parent_dir, child_dir)
    os.makedirs(trace_data_dir, exist_ok=True)
    return trace_data_dir

def single_glob(pattern):
    extracted_src_file_dir=glob(pattern)
    assert len(extracted_src_file_dir) == 1
    return extracted_src_file_dir[0]


if __name__ == "__main__":
    main()