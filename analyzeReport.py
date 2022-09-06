import os
import subprocess
from subprocess import Popen, PIPE
from openpyxl import Workbook
from openpyxl import load_workbook
from operator import attrgetter
import csv
import re

# OneView paths
pathToCodeletExtractorDir = "/host/localdisk/spyankov/codelet-extractor"
maqaoPath = '/host/localdisk/spyankov/cape-experiment-scripts/utils/MAQAO/maqao_new_2020'

# CloverLeaf paths
pathToAnalyzedBinary = "/host/localdisk/spyankov/CloverLeaf/clover_leaf"
pathToBenchmark = "/host/localdisk/spyankov/CloverLeaf"
LOOPFILEPATH = ""
LOOPFILENAME = ""
BASEFILENAME = ""
LOOPOBJNAME = ""
OBJDIR = "./obj" #pathToBenchmark + "/obj"
MPIOBJDIR = "./mpiobj" #pathToBenchmark + "/mpiobj"
PATHTOPIN = "/host/localdisk/spyankov/pin-3.22-98547-g7a303a835-gcc-linux"

# Global variables for segment boundaries and min/max accessed memory addresses
start_ds_addr = 0
end_ds_addr = 0
start_heap_addr = 0
end_heap_addr = 0
start_stack_addr = 0
end_stack_addr = 0
ds_min_addr = 0
ds_max_addr = 0
heap_min_addr = 0
heap_max_addr = 0
stack_min_addr = 0
stack_max_addr = 0

# Debug prints knob
isDebug = False

##################################################################################################
## Utility functions that move files, create or remove directories, and run other commands in bash
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

def makeCodeletDir():
    codeletDirCmd = "mkdir -p ./LoopExtractor_data/codelet_"
    fileName = LOOPFILENAME.split('.')
    codeletDirCmd += fileName[-2]
    runBashCmd(codeletDirCmd)

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

def removeLoopObjFile():
    rmCmd = "rm -r "
    rmCmd += OBJDIR
    rmCmd += "/"
    fileName = (LOOPFILEPATH.split('/'))[-1]
    objName = LOOPOBJNAME#getObjName(fileName)
    rmCmd += objName
    runBashCmd(rmCmd)
    rmMpiCmd = "rm -r "
    rmMpiCmd += MPIOBJDIR
    rmMpiCmd += "/"
    rmMpiCmd += objName
    runBashCmd(rmMpiCmd)

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

# Build and run the binary return the measurement output file dumped by MAQAO run
def run_and_measure():
    runMeasMaqao='LD_LIBRARY_PATH={}/lib:$LD_LIBRARY_PATH {}/maqao'.format(maqaoPath, maqaoPath)
    meaOutFile=os.path.join(maqaoPath, 'out.txt')
    myCmd='{} oneview -create-report=qprof -of=xlsx -binary={} -run_directory="{}" |tee {}'.format(runMeasMaqao, pathToAnalyzedBinary, pathToBenchmark, meaOutFile)
    # Uncomment to run real measurement
    #runBashCmd(myCmd)
    return meaOutFile

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
    return [int(firstLineNum)-2,int(secondLineNum)+2]

# Function that finds a full path to the loop file
# Currently, not working (returning the hardcoded global variable)
def findLoopPath(loop):
    pairOfNumbers = parseLineNumberString(loop[1])
    myCmd = "cd "+pathToBenchmark
    #os.system(myCmd)
    subprocess.check_call(myCmd,stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    wd = os.getcwd()
    os.chdir(pathToBenchmark)
    loopPath=subprocess.check_output("pwd").strip().decode()#"find ./ -name \""+loop[0]+"\"").strip().decode() #.strip().decode()
    os.chdir(wd)
    #print("Found a filename: "+loopPath)
    return LOOPFILEPATH

# Function that writes a csv file with a path to loopfile and loop line numbers
# This loop location file will be read in Rose tool to choose the loop to be extracted
def generateLoopLocFile(loopPath, lineNumbers):
    pairOfNumbers = parseLineNumberString(lineNumbers)
    row = [loopPath, pairOfNumbers[0], pairOfNumbers[1]]
    csvFileName = "tmpLoop.csv"
    with open(csvFileName, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)
    return ('./'+csvFileName)

# Running Rose tool that does in-situ extraction and generate all necessary source files for in-vitro extraction
### THIS WORKS ONLY FOR CLOVERLEAF
def extractLoop():
    myCmd = pathToCodeletExtractorDir
    myCmd += "/bin/LoopExtractor -I/usr/lib/x86_64-linux-gnu/openmpi/include -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -DUSE_OPENMP -lm "
    myCmd += LOOPFILEPATH
    runBashCmd(myCmd)

# Generation of an object file for some utilities necessary for running in-vitro extraction
### THIS WORKS FOR CLOVERLEAF OR OTHER BENCHMARKS THAT USE OBJECT FILES AS PART OF BUILDING PROCESS
def buildUtil():
    myCmd = "gcc -std=c++11 -c -o util.o -I. -I./LoopExtractor_data ./LoopExtractor_data/util.c"
    runBashCmd(myCmd)
    moveCmd = "mv util.o ./ExtractedLoop_objfiles"
    runBashCmd(moveCmd)

# Generating an object file of an extracted (in-situ) loop
### THIS WORKS ONLY FOR CLOVERLEAF
def buildLoopFile():
    myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/"
    myCmd += LOOPFILENAME
    myCmd += " -o ./ExtractedLoop_objfiles/"
    myCmd += (LOOPFILENAME.split('.'))[-2]
    myCmd += ".o"
    runBashCmd(myCmd)
    
# Parsing string with a source file name so to generate object file name out of it (by replacing an extension)
### THIS WORKS FOR CLOVERLEAF OR OTHER BENCHMARKS THAT USE OBJECT FILES AS PART OF BUILDING PROCESS
def getObjName(sourceFileName):
    fileName = sourceFileName.split('.')
    objFileName = fileName[-2] + ".o"
    return objFileName

# Function that receives loop file names that were generated during the execution of Rose tool
def getLoopFileNames():
    with open('/tmp/loopFileNames.txt') as loopFileNames: 
        lines = loopFileNames.readlines()
        baseStr = lines[0]
        loopStr = lines[1]
        global BASEFILENAME
        BASEFILENAME = baseStr[:len(baseStr)-1]
        global LOOPFILENAME
        LOOPFILENAME = loopStr[:len(loopStr)-1]
        global LOOPOBJNAME
        LOOPOBJNAME = getObjName((LOOPFILEPATH.split('/'))[-1])

# Generation of a binary out of previously generated object files
### THIS WORKS ONLY FOR CLOVERLEAF
def buildObjFiles():
    myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -fopenmp -DUSE_OPENMP "
    myCmd += OBJDIR
    myCmd += "/*.o " 
    myCmd += MPIOBJDIR
    myCmd += "/*.o ./ExtractedLoop_objfiles/*.o "
    myCmd += "./src/clover_leaf.cc -o "
    myCmd += "./clover_leaf"
    runBashCmd(myCmd)

# Building a benchmark where base file was replaced with TRACE source file
# to trace memory access addresses
### THIS WORKS ONLY FOR CLOVERLEAF
def buildTraceSourceFile():
    removeLoopObjFile()
    myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/codelet_"
    fileName = LOOPFILENAME.split('.')
    myCmd += fileName[-2]
    myCmd += "/trace_"+BASEFILENAME
    myCmd += " -o ./ExtractedLoop_objfiles/"
    myCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1]))
    runBashCmd(myCmd)
    buildObjFiles()

# Running pintool to trace/save memory addresses
### THIS WORKS ONLY FOR CLOVERLEAF
def runPin(passNum):
    myCmd = PATHTOPIN
    myCmd += "/pin -t "
    myCmd += PATHTOPIN
    #This line is used for more modern pintool (HuskyFuncTrace)
    #myCmd += "/source/tools/HuskyFuncTrace/obj-intel64/HuskyFuncTrace.so -start_ds_addr " 
    myCmd += "/source/tools/HuskyTool/obj-intel64/HuskyTool.so -start_ds_addr "
    myCmd += str(start_ds_addr)
    myCmd += " -end_ds_addr "
    myCmd += str(end_ds_addr)
    myCmd += " -start_heap_addr "
    myCmd += str(start_heap_addr)
    myCmd += " -end_heap_addr "
    myCmd += str(end_heap_addr)
    myCmd += " -start_stack_addr "
    myCmd += str(start_stack_addr)
    myCmd += " -end_stack_addr "
    myCmd += str(end_stack_addr)
    myCmd += " -loop_name "
    fileName = LOOPFILENAME.split('.')
    myCmd += fileName[-2]
    #This line is used for more modern pintool (HuskyFuncTrace)
    #myCmd += " -path_to_callgraph ./LoopExtractor_data/callgraphResult.extr -- ./clover_leaf |& tee /tmp/out.txt" 
    if passNum == 0:
        myCmd += " -- ./clover_leaf >> /tmp/out.txt"
    elif passNum == 1:
        myCmd += " -- ./clover_leaf "# >> /tmp/out.trace.txt"
    runBashCmd(myCmd)

# Parsing text file with collected boundaries of heap, stack, data segment
def getSegmentVars():
    tmpOutFile = open("/tmp/out.txt", "r")
    for line in tmpOutFile:
        if re.search("STACK BEGIN", line):
            var = (line.split(": "))[-1]
            global start_stack_addr
            start_stack_addr = "0x"+(var[:len(var)-1])
        elif re.search("STACK END", line):
            var = (line.split(": "))[-1]
            global end_stack_addr
            end_stack_addr = "0x"+(var[:len(var)-1])
        elif re.search("HEAP START", line):
            var = (line.split(": "))[-1]
            global start_heap_addr
            start_heap_addr = "0x"+(var[:len(var)-1])
        elif re.search("HEAP END", line):
            var = (line.split(": "))[-1]
            global end_heap_addr
            end_heap_addr = "0x"+(var[:len(var)-1])
        elif re.search("DS START", line):
            var = (line.split(": "))[-1]
            global start_ds_addr
            start_ds_addr = "0x"+(var[:len(var)-1])
        elif re.search("DS END", line):
            var = (line.split(": "))[-1]
            global end_ds_addr
            end_ds_addr = "0x"+(var[:len(var)-1])
    tmpOutFile.close()

# Parsing text file with collected minimal and maximal ACCESSES addresses of heap, stack, data segment
def getMinMaxVars():
    traceOutFile = open("/tmp/out.trace.txt", "r")
    for line in traceOutFile:
        if re.search("Minimal stack segment address", line):
            var = (line.split(": "))[-1]
            global stack_min_addr
            stack_min_addr = "0x"+(var[:len(var)-1])
        elif re.search("Maximal stack segment address", line):
            var = (line.split(": "))[-1]
            global stack_max_addr
            stack_max_addr = "0x"+(var[:len(var)-1])
        elif re.search("Minimal heap segment address", line):
            var = (line.split(": "))[-1]
            global heap_min_addr
            heap_min_addr = "0x"+(var[:len(var)-1])
        elif re.search("Maximal heap segment address", line):
            var = (line.split(": "))[-1]
            global heap_max_addr
            heap_max_addr = "0x"+(var[:len(var)-1])
        elif re.search("Minimal data segment address", line):
            var = (line.split(": "))[-1]
            global ds_min_addr
            ds_min_addr = "0x"+(var[:len(var)-1])
        elif re.search("Maximal data segment address", line):
            var = (line.split(": "))[-1]
            global ds_max_addr
            ds_max_addr = "0x"+(var[:len(var)-1])
    traceOutFile.close()
    addressFile = open("addresses.h", "w")
    minStackLine = "#define min_stack_address ((unsigned char *) "
    minStackLine += stack_min_addr
    minStackLine += ")\n"
    maxStackLine = "#define max_stack_address ((unsigned char *) "
    maxStackLine += stack_max_addr
    maxStackLine += ")\n"
    minHeapLine = "#define min_heap_address ((unsigned char *) "
    minHeapLine += heap_min_addr
    minHeapLine += ")\n"
    maxHeapLine = "#define max_heap_address ((unsigned char *) "
    maxHeapLine += heap_max_addr
    maxHeapLine += ")\n"
    minDsLine = "#define min_ds_address ((unsigned char *) "
    minDsLine += ds_min_addr
    minDsLine += ")\n"
    maxDsLine = "#define max_ds_address ((unsigned char *) "
    maxDsLine += ds_max_addr
    maxDsLine += ")\n"
    L = [minStackLine, maxStackLine, minHeapLine, maxHeapLine, minDsLine, maxDsLine]
    addressFile.writelines(L)
    addressFile.close()

# Running TRACE inside of a pintool
# First pass collects segment boundaries (minimal and maximal addresses stack, heap, data segment)
# Second pass traces minimal and maximal ACCESSES addresses of stack, heap, data segment
def runTrace():
    removeTmpFiles()
    # First pass
    runPin(0)
    getSegmentVars()
    # Second pass
    runPin(1)
    getMinMaxVars()

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
def buildSaveSourceFile():
    myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data -c ./LoopExtractor_data/codelet_"
    fileName = LOOPFILENAME.split('.')
    myCmd += fileName[-2]
    myCmd += "/save_"+BASEFILENAME
    myCmd += " -o ./ExtractedLoop_objfiles/"
    myCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1])
    runBashCmd(myCmd)
    buildObjFiles()

# Building a driver file from RESTORE source file and generate a binary of a codelet
### THIS WORKS ONLY FOR CLOVERLEAF
def buildRestoreSourceFile():
    buildBenchmark()
    rmCmd = "rm ./ExtractedLoop_objfiles/"
    rmCmd += LOOPOBJNAME#getObjName((LOOPFILEPATH.split('/'))[-1])
    runBashCmd(rmCmd)
    myCmd = "mpic++ -std=c++11 -Wall -Wpedantic -g -Wno-unknown-pragmas -O3 -march=native -lm -fopenmp -DUSE_OPENMP -I. -I./src -I./src/adaptors -I./src/kernels -I./LoopExtractor_data "
    myCmd += OBJDIR
    myCmd += "/*.o " 
    myCmd += MPIOBJDIR
    myCmd += "/*.o ./ExtractedLoop_objfiles/*.o ./LoopExtractor_data/codelet_"
    fileName = LOOPFILENAME.split('.')
    myCmd += fileName[-2]
    myCmd += "/restore_" + BASEFILENAME
    myCmd += " -o ./restore"
    runBashCmd(myCmd)

# Running SAVE inside of a pintool
def runSave():
    runPin(1)

# Building TRACE, SAVE, and RESTORE source files and running them to save datafiles
def generateCodelet():
    copyUtilFiles()
    getLoopFileNames()
    makeCodeletDir()
    buildUtil()
    buildLoopFile()
    buildTraceSourceFile()
    print("Tracing memory addresses")
    runTrace()
    print("FINISHED tracing memory addresses!")
    buildSaveSourceFile()
    print("Saving data from traced memory addresses")
    runSave() 
    print("FINISHED saving the data")
    buildRestoreSourceFile()

# Building the benchmark from scratch
### THIS WORKS ONLY FOR CLOVERLEAF
def buildBenchmark():
    myCmd = "make clean\nmake COMPILER=GNU USE_OPENMP=1\n"
    runBashCmd(myCmd)

# Generate config.h header file and write instance number 0 there
# Instance number is used during In-Vitro extraction to choose which execution instance of the loop to save (and restore as a codelet)
def initiateConfig(instanceNum):
    configFile = open('config.h', 'w')
    instLine = "int extr_instance = 0;\n"
    configFile.write(instLine)
    configFile.close()
    myCmd = "mv config.h ./LoopExtractor_data"
    runBashCmd(myCmd)

# Function responsible for the extraction process
### THIS WORKS FOR SPECIFIC SOURCE FILES FROM CLOVERLEAF
def runExtractor(loopsToExtract):
    # Creating Loop Extractor working directory
    createLoopExtrWorkingDirectory()
    initiateConfig(0)
    # Currently running it on a specific example, ignoring the parameter loopsToExtract
    # When parsing of OneView report will be finished, replace the lines of code above with a commented loop
    #loop = ["update_halo.cc","37-37"]
    loop = ["clover.cc","81-81"]
    global LOOPFILEPATH
    #LOOPFILEPATH = "/host/localdisk/spyankov/CloverLeaf/src/update_halo.cc"
    LOOPFILEPATH = "/host/localdisk/spyankov/CloverLeaf/src/clover.cc"
    loopPath = findLoopPath(loop) #NOT WORKING AT THE MOMENT, RETURNING THE LOOPFILEPATH GLOBAL VARIABLE
    # Generating a Loop Location file with info about a loop (path to a file and line number of a loop) 
    # that should be extracted to the working directory
    loopLocFilePath = generateLoopLocFile(loopPath, loop[1])
    moveFile(loopLocFilePath, "./LoopExtractor_data")
    # Running Rose tool
    extractLoop()
    # Saving data and build all necessary source files to generate a codelet  
    generateCodelet()

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

# Function that runs OneView and Chooses loops that should be extracted by parsing OneView report
def runOneView():
    pathToReport = run_and_measure()
    loopsToExtract = parseReport(pathToReport)
    return loopsToExtract



## PREPARE
print("Preparing the environment for the extraction")
prepareForExtraction()
print("FINISHED preparing the environment!")

## ONEVIEW REPORT
print("Running OneView")
loopsToExtract = runOneView()
print("FINISHED running OneView!")

## EXTRACTING A CODELET
print("Extracting a codelet")
runExtractor(loopsToExtract)
print("FINISHED the extraction of a codelet!")
