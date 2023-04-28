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

SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))

# OneView paths
#prefix = "/host/localdisk/cwong29/working/codelet_extractor_work"
#prefix = "/localdisk/cwong29/working/codelet_extractor_work"
prefix = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

#pathToCodeletExtractorDir = "/host/localdisk/spyankov/codelet-extractor"
#pathToCodeletExtractorDir = f"{prefix}/codelet-extractor"
#maqaoPath = f'{prefix}/cape-experiment-scripts/utils/MAQAO/maqao_new_2020'

PATHTOPIN = os.path.join(SCRIPT_DIR, "..", "pin")
ADVISOR_VARS_SH = '/host/opt/intel/oneapi/advisor/2023.0.0/advisor-vars.sh'

LOOP_EXTRACTOR_PATH=os.path.join(SCRIPT_DIR, "bin", "LoopExtractor")

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
def runCmdGetRst(myCmd, cwd, env=os.environ.copy()):
    result = subprocess.run(myCmd, shell=True, env=env, cwd=cwd, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def runCmd(myCmd, cwd, env=os.environ.copy(), verbose=False):
    subprocess.run(myCmd, shell=True, env=env, cwd=cwd, capture_output=not verbose)
    
def runBashCmd(myCmd):
    #os.system(myCmd)
    try:
        subprocess.check_call(myCmd,stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
    except:
        if isDebug:
            print("Error while running the command {} ", myCmd)

def turnOffAddressRandomization():
    myCmd = "echo 0 |sudo tee /proc/sys/kernel/randomize_va_space"
    runBashCmd(myCmd)
##################################################################################################


# Function that writes a csv file with a path to loopfile and loop line numbers
# This loop location file will be read in Rose tool to choose the loop to be extracted
def generateLoopLocFile(loopPath, begin_line, end_line, outdir="."):
    #pairOfNumbers = parseLineNumberString(lineNumbers)
    #begin_line = pairOfNumbers[0]
    #end_line = pairOfNumbers[1]
    # expected format of main src info [ '/host/...', '152' ]
    row = [loopPath, begin_line, end_line]
    #main_src_info = main_src_info.split(':')
    #main_row = [main_src_info[0], int(main_src_info[1]), int(main_src_info[1])]
    csvFileName = "tmpLoop.csv"
    with open(os.path.join(outdir, csvFileName), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)
        #csvwriter.writerow(main_row)
    pass
    #return ('./'+csvFileName)

def getLoopFileNames(loop_name_file):
    with open(loop_name_file) as loopFileNames: 
        lines = loopFileNames.readlines()
        baseStr = lines[0]
        loopStr = lines[1]
        restoreStr = lines[2]
    return baseStr.strip(), loopStr.strip(), restoreStr.strip()

# Generate config.h header file and write instance number 0 there
# Instance number is used during In-Vitro extraction to choose which execution instance of the loop to save (and restore as a codelet)
def initiateConfig(outdir, instanceNum=0):
    configFile = open(os.path.join(outdir, 'lore_config.h'), 'w')
    #instLine = f"extern int extr_instance = {instanceNum};\n"
    instLine = f"extern int extr_instance;\n"
    configFile.write(instLine)
    configFile.close()

def load_advisor_env():
    #script = os.path.join(compiler_dir, 'Linux/intel64/load.sh')
    #script = '/nfs/site/proj/openmp/compilers/intel/19.0/Linux/intel64/load.sh'
    pipe = subprocess.Popen(f"/bin/bash -c 'source {ADVISOR_VARS_SH} --force && env'", stdout=subprocess.PIPE, shell=True)
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
    clean = True
    build_app=True
    spec_run = True
    #spec_run = False

    # TODO: mark these command line arguments
    binary='525.x264_r'
    #binary='clover_leaf'
    #binary='bt.c_compute_rhs_line1892_0'
    if binary == '525.x264_r':
        cmakelist_dir=os.path.join(prefix, 'SPEC2017/llvm-test-suite')
        src_dir=os.path.join(prefix, 'SPEC2017/benchmark')
        cmake_flags = f'-DTEST_SUITE_SUBDIRS=External/SPEC/CINT2017rate -DTEST_SUITE_SPEC2017_ROOT={src_dir} -DCMAKE_C_COMPILER=icx -DTEST_SUITE_COLLECT_CODE_SIZE=OFF'
        cmake_flags = f'-DTEST_SUITE_SUBDIRS=External/SPEC/CINT2017rate -DTEST_SUITE_SPEC2017_ROOT={src_dir} -DCMAKE_C_COMPILER=icx -DCMAKE_C_FLAGS="-g -DSPEC" -DCMAKE_CXX_FLAGS="-g -DSPEC" -DTEST_SUITE_COLLECT_CODE_SIZE=OFF'
        #cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-g" -DCMAKE_CXX_FLAGS="-DUSE_OPENMP"'
        #cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g"'

        app_data_file=os.path.join(prefix, 'SPEC2017/benchmark/benchspec/CPU/525.x264_r/run/run_base_test_myTest.0000/BuckBunny.yuv')

        app_flags = ' --dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720'
    elif binary == 'clover_leaf':
        cmakelist_dir=os.path.join(prefix,'CloverLeaf')
        cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-DUSE_OPENMP"'
        cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-DUSE_OPENMP -g" -DCMAKE_C_FLAGS="-g"'
        cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-cxx=icpx -DUSE_OPENMP -g" -DCMAKE_C_FLAGS="-g"'

        app_data_file = os.path.join(cmakelist_dir, 'clover.in')

        app_flags = ''
    elif binary == 'bt.c_compute_rhs_line1892_0':
        cmakelist_dir=os.path.join(prefix,'qaas-demo-lore-codelets')
        cmake_flags = f'-DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g"'
        app_data_file = os.path.join(cmakelist_dir, 'src','all','NPB_2.3-OpenACC-C','BT','bt.c_compute_rhs_line1892_0','codelet.data')
        app_flags = ''
    else:
        return

    top_n = 21
    top_n = 1
    perform_extraction_steps(top_n, clean, build_app, binary, cmakelist_dir, cmake_flags, app_data_file, app_flags)

def perform_extraction_steps(top_n, clean, build_app, binary, cmakelist_dir, cmake_flags, app_data_file, app_flags):
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
    main_src_file_info, _ = runCmdGetRst(f'nm -a {binary} | grep " main$" | cut -d " " -f 1 | xargs addr2line -e {binary}', cwd=profile_data_dir, env=adv_env)
    #app_cmd = f'./{binary}'
    app_cmd = f'./{binary}{app_flags}'
    #mockup_profile_csv = '/host/localdisk/cwong29/working/codelet_extractor_work/SPEC2017/extractor_work/525.x264_r/168-238-9156/profile_data/profile.csv'
    mockup_profile_csvs = {'./clover_leaf': '/host/localdisk/cwong29/working/codelet_extractor_work/extractor_work/clover_leaf/168-245-0832/profile_data/profile.csv', 
                           './525.x264_r --dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720': '/host/localdisk/cwong29/working/codelet_extractor_work/SPEC2017/extractor_work/525.x264_r/168-238-9156/profile_data/profile.csv',
                           './bt.c_compute_rhs_line1892_0':'/host/localdisk/cwong29/working/codelet_extractor_work/extractor_work/bt.c_compute_rhs_line1892_0/168-252-4181/profile_data/profile.csv'}
    mockup_profile_csvs = {}
    mockup_profile_csv = mockup_profile_csvs[app_cmd] if app_cmd in mockup_profile_csvs else None
    if not mockup_profile_csv:
        runCmd(f'advixe-cl --collect survey --project-dir {adv_proj_dir} -- {app_cmd}', 
           cwd=profile_data_dir, env=adv_env, verbose=True)

        profile_csv = os.path.join(profile_data_dir, 'profile.csv')
        runCmd(f'advisor --report joined --project-dir={adv_proj_dir} > {profile_csv}',
           cwd=profile_data_dir, env=adv_env, verbose=True)
    else:
        profile_csv = mockup_profile_csv
    profile_df = pd.read_csv(profile_csv, skiprows=1, delimiter=',')
    # Select loops only
    loop_profile_df = profile_df[profile_df['function_instance_type'] == 2]
    loop_profile_df = loop_profile_df.sort_values(by='self_time', ascending=False)

    for idx in range(0, top_n):
        extract_codelet(binary, cmakelist_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, 
                        cmake_flags, loop_profile_df, idx, prefix, app_flags, app_data_file, main_src_file_info)
    print("DONE")

def link_app_data_file(profile_data_dir, app_data_file):
    os.symlink(app_data_file, os.path.join(profile_data_dir, os.path.basename(app_data_file)))


def extract_codelet(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, profile_df, 
                    idx, prefix, app_flags, app_data_file, main_src_info):
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
    #loop = [ source_file ,81+3, 81+10]
    #loop = [ source_file ,43, 74]
    loop = [ source_file , source_line, source_line]
    generateLoopLocFile(loop[0], loop[1], loop[2], loop_extractor_data_dir)
    main_src_info = main_src_info.split(':')
    main_source_file = main_src_info[0]

    sources = sorted({source_file, main_source_file})

    source_row_list = []
    for source_file in sources:
        row_dict = {'orig_src':source_file}
        row_dict['base_src'], row_dict['loop_src'], row_dict['replay_src'], row_dict['global_vars'] = run_extractor(build_dir, extractor_work_dir, loop_extractor_data_dir, prefix, source_file)
        source_row_list.append(row_dict)
    extracted_sources = pd.DataFrame(source_row_list, columns=['orig_src', 'base_src', 'loop_src', 'replay_src', 'global_vars'])

    #name_map, loop_file, util_h_file, util_c_file, segment_info, save_data_dir, save_pointers_h_file, defs_h_file = capture_data(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, app_flags, app_data_file, full_source_path, source_path, extracted_sources)
    cere_src_folder = os.path.join(SCRIPT_DIR, 'src', 'cere')
    cere_out_dir, full_trace_binary = capture_data(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, 
                                app_flags, app_data_file, full_source_path, source_path, extracted_sources, cere_src_folder)

    instance_num = 1
    loop_srcs = [f for f in extracted_sources['loop_src'] if f]

    restore_work_dir = ensure_dir_exists(extractor_work_dir, 'replay_data')
    extracted_codelets_dir = ensure_dir_exists(restore_work_dir, 'codelet')
    with open(os.path.join(extracted_codelets_dir, 'CMakeLists.txt'), "w") as top_cmakelist:
        print(f"cmake_minimum_required(VERSION 3.2.0)", file=top_cmakelist)
        print(f"project({binary})", file=top_cmakelist)
        for loop_src, replay_loop_src, base_src, global_vars in zip(extracted_sources['loop_src'],
                                             extracted_sources['replay_src'], 
                                             extracted_sources['base_src'],
                                             extracted_sources['global_vars']):
            if not loop_src:
                continue  # Skip empty loop info
            loop_filename = os.path.basename(loop_src)
            loop_name = os.path.splitext(loop_filename)[0]

            restore_binary=f'replay_{loop_name}'
            extracted_loop_dir = ensure_dir_exists(extracted_codelets_dir, loop_name)
            print(f"add_subdirectory({loop_name})\n", file=top_cmakelist)
            restore_include_dir = ensure_dir_exists(extracted_loop_dir, 'include')
            restore_src_dir = ensure_dir_exists(extracted_loop_dir, 'src')
            restore_data_root_dir = ensure_dir_exists(extracted_loop_dir, 'data')

            dump_name = re.search(r"dump\(\"([^\"]*)", 
                                  open(os.path.join(loop_extractor_data_dir, base_src)).read()).group(1)
            restore_data_dir = ensure_dir_exists(restore_data_root_dir, f"dumps/{dump_name}/{instance_num}")
            cere_dump_dir = os.path.join(cere_out_dir, "dumps", dump_name, str(instance_num))
            # Copy .map files
            shutil.copy2(os.path.join(cere_dump_dir, "core.map"), restore_data_dir)
            shutil.copy2(os.path.join(cere_dump_dir, "hotpages.map"), restore_data_dir)
            obj_s_file = "objs.S"
            restore_linker_section_flags=[]
            with open(os.path.join(restore_src_dir, obj_s_file), "w") as obj_s_f:
                data_rel_src_dir = os.path.relpath(restore_data_dir, restore_src_dir)
                for memdump_file in glob(f'{cere_dump_dir}/*.memdump'):
                    shutil.copy2(memdump_file, restore_data_dir)
                    # Drop prefix directory name and also extension
                    base_memdump_file = os.path.basename(memdump_file)
                    addr = os.path.splitext(base_memdump_file)[0]
                    print(f'.section s{addr}, "aw"', file=obj_s_f)
                    # Use relative path assuming build under directory extracted_loop_dir
                    print(f'.incbin "{data_rel_src_dir}/{base_memdump_file}"', file=obj_s_f)
                    restore_linker_section_flags.append(f" -Wl,--section-start=s{addr}=0x{addr}")
            replay_h_file = os.path.join(cere_src_folder, 'replay.h')
            replay_c_file = os.path.join(cere_src_folder, 'replay_driver.c')
            shutil.copy2(replay_c_file, restore_src_dir)
            shutil.copy2(replay_h_file, restore_include_dir)
            shutil.copy2(os.path.join(loop_extractor_data_dir, loop_src), restore_src_dir)
            shutil.copy2(os.path.join(loop_extractor_data_dir, replay_loop_src), restore_src_dir)

            global_linker_flags = []
            for global_var in global_vars:
                addr_cmd = f"objdump -t {full_trace_binary}|grep '{global_var}$'|awk '{{print $1}}'"
                # cwd should not matter
                rst,_ = runCmdGetRst(addr_cmd, cwd = extractor_work_dir)
                global_linker_flags.append(f" -Wl,-defsym,{global_var}=0x{rst}")
                
            restore_linker_flags = "-Wl,--section-start=.text=0x60004000 -Wl,--section-start=.init=0x60000000" \
                +"".join(restore_linker_section_flags)+"".join(global_linker_flags) +" -Wl,-z,now"
            name_map = { 'restore_binary': restore_binary, 'loop_src': loop_src, 'replay_loop_src': replay_loop_src, 
                        'obj_s': obj_s_file, 'restore_linker_flags': restore_linker_flags }
            instantiate_cmakelists_file(name_map, in_template = 'CMakeLists.restore.template', 
                                    out_instantiated_file=os.path.join(extracted_loop_dir, 'CMakeLists.txt'))


    # Build and run
    extracted_codelet_build_dir = ensure_dir_exists(restore_work_dir, 'build')
    extracted_codelets_run_dir = ensure_dir_exists(restore_work_dir, 'run')
    for loop_src in loop_srcs:
        # Try to build restore (extracted codelete)
        loop_filename = os.path.basename(loop_src)
        loop_name = os.path.splitext(loop_filename)[0]
        restore_binary=f'replay_{loop_name}'
        restore_cmake_flags = f'-DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx -DCMAKE_CXX_FLAGS="-g -D__RESTORE_CODELET__" -DCMAKE_C_FLAGS="-g -D__RESTORE_CODELET__"'
        #run_cmake2(restore_binary, restore_work_dir, extracted_codelet_dir, extracted_codelet_build_dir, restore_cmake_flags)
        run_cmake(extracted_codelets_dir, extracted_codelet_build_dir, restore_work_dir, restore_cmake_flags, restore_binary)

        # Now can run built extracted codelet
        codelet_run_dir = ensure_dir_exists(extracted_codelets_run_dir, loop_name)
        os.symlink(os.path.join(extracted_codelet_build_dir, loop_name, restore_binary), os.path.join(codelet_run_dir, restore_binary))
        extracted_loop_dir = ensure_dir_exists(extracted_codelets_dir, loop_name)
        restore_data_root_dir = ensure_dir_exists(extracted_loop_dir, 'data')
        # Should also sofelink cere directory here
        run_extracted_loop(f'./{restore_binary}', codelet_run_dir, restore_data_root_dir)

def run_extracted_loop(cmd, codelet_run_dir, cere_data_dir, env=os.environ.copy()):
    env['CERE_WORKING_PATH'] = cere_data_dir
    runCmd(cmd, cwd=codelet_run_dir, env=env, verbose=True)

def run_extractor(build_dir, extractor_work_dir, loop_extractor_data_dir, prefix, source_file):
    src_folder=os.path.dirname(source_file)
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
                    command_parts.insert(1, f"-cxx={LOOP_EXTRACTOR_PATH}")
                else:
                    # TODO: fix hardcoded
                    compiler_full_path = shutil.which("icx")
                    command_parts = [LOOP_EXTRACTOR_PATH if x == compiler_full_path else x for x in command_parts]
                loop_extractor_command = " ".join(command_parts+['--extractwd', extractor_work_dir, '--extractsrcprefix', prefix])
                    
                if os.path.basename(compiler).startswith("mpi"):
                    # MPI compilers
                    pass 
                else:
                    pass


    # Extractor loop using in-situ extractor
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = env['LD_LIBRARY_PATH']+':/usr/lib/jvm/java-11-openjdk-amd64/lib/server'
    env['OMP_NUM_THREADS']="1"
    
    #runCmd(loop_extractor_command, cwd=extractor_work_dir, env=env, verbose=True)

    #data_dir_symlink = os.path.join(command_directory, os.path.basename(loop_extractor_data_dir))
    #if os.path.islink(data_dir_symlink):
    #    os.unlink(data_dir_symlink)
    #os.symlink(loop_extractor_data_dir, data_dir_symlink)
    runCmd(loop_extractor_command, cwd=command_directory, env=env, verbose=True)
    basefilename, loopfilename, restore_src_file = getLoopFileNames(
        os.path.join(loop_extractor_data_dir, 'loopFileNames.txt'))
    global_vars = []
    if loopfilename:
        with open(os.path.join(loop_extractor_data_dir, 'globalVarNames.txt')) as gf:
            lines = gf.readlines()
            global_vars = [l.replace('"','').strip('\n') for l in lines ] 
    return basefilename,loopfilename,restore_src_file, global_vars

def capture_data(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, 
                 loop_extractor_data_dir, cmake_flags, app_flags, app_data_file, 
                 full_source_path, source_path, 
                # basefilename, loopfilename, 
                 extracted_sources, cere_src_folder):
    cmake_extractor_src_dir = ensure_dir_exists(src_dir, 'extractor_src')
    cmake_extractor_include_dir = ensure_dir_exists(src_dir, 'extractor_include')
    # Will use extracted_sources
    def collect_src_for_folder(folder):
        selected_rows = extracted_sources[extracted_sources['orig_src'].apply(lambda x: os.path.dirname(x) == folder)]
        return [f for f in selected_rows['loop_src'] if f] + [f for f in selected_rows['base_src'] if f] 


    # name_map = { "loop_src" : loopfilename, "binary" : binary, 
    #             "base_src": basefilename, "orig_src_path": full_source_path, 
    #             "orig_src_folder": os.path.dirname(source_path)}
    # Need to replace original sources ('orig_src' column) by their base ('base_src')
    # and loop ('loop_src') source code.  Need to make sure base and loop source
    # has original source folder in their include path
    orig_src_folders = sorted({os.path.dirname(s) for s in extracted_sources['orig_src']})
    src_for_folder_dict = {folder : collect_src_for_folder(folder) for folder in orig_src_folders}
    
    trace_binary=f'trace_{binary}'

    name_map = { "orig_src_files" : extracted_sources['orig_src'],
                 "orig_src_folders" : orig_src_folders,
                 "srcs_for_folder": src_for_folder_dict,
                 "binary": binary, "trace_binary": trace_binary }
    update_app_cmakelists_file(src_dir, name_map)

    #trace_src_file = single_glob(f'{extractor_codelet_src_dir}/trace_*')
    for file in list(extracted_sources['loop_src']) + list(extracted_sources['base_src']):
        if file: 
            full_file_path = os.path.join(loop_extractor_data_dir, file)
            shutil.copy2(full_file_path, cmake_extractor_src_dir)
            
    # trace_src_file = os.path.join(loop_extractor_data_dir, basefilename)
    # shutil.copy2(trace_src_file, cmake_extractor_src_dir)

    # loop_file = os.path.join(loop_extractor_data_dir, loopfilename)
    # shutil.copy2(loop_file, cmake_extractor_src_dir)


    initiateConfig(cmake_extractor_include_dir)

    tracee_h_file = os.path.join(cere_src_folder, 'tracee.h')
    shutil.copy2(tracee_h_file, cmake_extractor_include_dir)

    types_h_file = os.path.join(cere_src_folder, 'types.h')
    shutil.copy2(types_h_file, cmake_extractor_include_dir)

    util_h_file = os.path.join(SCRIPT_DIR, 'src', 'tracer', 'util.h')
    shutil.copy2(util_h_file, cmake_extractor_include_dir)
    util_c_file = os.path.join(SCRIPT_DIR, 'src', 'tracer', 'util.c')
    shutil.copy2(util_c_file, cmake_extractor_src_dir)
    # defs.h needed by util.c
    defs_h_file = os.path.join(SCRIPT_DIR, 'src', 'tracer', 'defs.h')
    shutil.copy2(defs_h_file, cmake_extractor_src_dir)
    

    tracer_dir = ensure_dir_exists(extractor_work_dir, 'tracer_data')
    tracer_run_dir = ensure_dir_exists(tracer_dir, 'run')
    link_app_data_file(tracer_run_dir, app_data_file)
    segment_info = SegmentInfo(tracer_dir)
    segment_info.generate_address_h()
    shutil.copy2(segment_info.tracer_out_addresses_h_file, cmake_extractor_include_dir)

    run_cmake(src_dir, build_dir, run_cmake_dir, f'-DBUILD_TRACE=ON {cmake_flags}', trace_binary)

    full_trace_binary = os.path.join(build_dir, trace_binary)
    run_trace_binary = f'{full_trace_binary}{app_flags}'
    runCmd(run_trace_binary, cwd=tracer_run_dir, verbose=True)

    cere_out_dir = os.path.join(tracer_run_dir, ".cere")
    return cere_out_dir, full_trace_binary

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
