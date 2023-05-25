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
from abc import ABC, abstractmethod
import csv
import re
import datetime
from Cheetah.Template import Template
import argparse

SCRIPT_DIR=os.path.dirname(os.path.abspath(__file__))


# OneView paths
#prefix = "/host/localdisk/cwong29/working/codelet_extractor_work"
#prefix = "/localdisk/cwong29/working/codelet_extractor_work"
PREFIX = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

#pathToCodeletExtractorDir = "/host/localdisk/spyankov/codelet-extractor"
#pathToCodeletExtractorDir = f"{prefix}/codelet-extractor"
#maqaoPath = f'{prefix}/cape-experiment-scripts/utils/MAQAO/maqao_new_2020'

PATHTOPIN = os.path.join(SCRIPT_DIR, "..", "pin")
ADVISOR_VARS_SH = '/host/opt/intel/oneapi/advisor/2023.0.0/advisor-vars.sh'
OV_PATH='/nfs/site/proj/alac/software/UvsqTools/20221206/bin/maqao'
OV_PATH='/nfs/site/proj/alac/software/UvsqTools/20230504/bin/maqao'

LOOP_EXTRACTOR_PATH=os.path.join(SCRIPT_DIR, "bin", "LoopExtractor")

# Debug prints knob
isDebug = False

##################################################################################################
## Utility functions that move files, create or remove directories, and run other commands in bash
def runCmdGetRst(myCmd, cwd, env=os.environ.copy()):
    result = run_subprocess_run(myCmd, cwd, env, capture_output = True, text=True)
    return result.stdout.strip(), result.stderr.strip()

def runCmd(myCmd, cwd, env=os.environ.copy(), verbose=False, throwException=False):
    run_subprocess_run(myCmd, cwd, env, capture_output = not verbose, text=False, throwException = throwException)

def run_subprocess_run(myCmd, cwd, env, capture_output, text=False, throwException=False):
    result = subprocess.run(myCmd, shell=True, env=env, cwd=cwd, capture_output=capture_output, text=text)
    if throwException and result.returncode != 0:
        raise Exception(f'Non-zero return code in execution: {result.returncode}')
    else:
        return result
    
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


def generateLoopLocFileMulti(loopPaths, begin_lines, end_lines, outdir="."):
    csvFileName = "tmpLoop.csv"
    with open(os.path.join(outdir, csvFileName), 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        for loopPath, begin_line, end_line in zip(loopPaths, begin_lines, end_lines):
            csvwriter.writerow([loopPath, begin_line, end_line])

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
    #return ('./'+csvFileName)

def getLoopFileNames(loop_name_file):
    loop_file_df = pd.read_csv(loop_name_file, names=['type', 'filename'])
    baseStr = loop_file_df[loop_file_df['type'] =='BASE']['filename'].item().strip()
    loopStr = [ls.strip() for ls in loop_file_df[loop_file_df['type'] =='LOOP']['filename']]
    restoreStr = [rs.strip() for rs in loop_file_df[loop_file_df['type'] =='RESTORE']['filename']]
    return baseStr, loopStr, restoreStr
    # with open(loop_name_file) as loopFileNames: 
    #     lines = loopFileNames.readlines()
    #     baseStr = lines[0]
    #     loopStr = lines[1]
    #     restoreStr = lines[2]
    # return baseStr.strip(), loopStr.strip(), restoreStr.strip()

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

class Extraction(ABC):
    def __init__(self, binary, build_app, clean):
        self.binary = binary
        self.build_app = build_app
        self.clean = clean


    @property
    @abstractmethod
    def mode(self):
        pass

    @property
    @abstractmethod
    def insitu_libs(self):
        pass
        
    def perform_replay(self):
        pass

    def perform_extraction_steps(self, top_n, cmakelist_dir, cmake_flags, app_data_files, app_flags):
        timestamp_str, run_cmake_dir = self.perform_folder_setup(cmakelist_dir)

        build_dir, bottom_cmake_folder = self.perform_app_build(cmakelist_dir, cmake_flags, run_cmake_dir)

        main_src_file_info, loop_profile_df = self.perform_profile_step(app_data_files, app_flags, timestamp_str, build_dir)

        self.perform_codelet_extraction(build_dir, loop_profile_df, 0, PREFIX, main_src_file_info)

        self.perform_insitu_steps(cmakelist_dir, bottom_cmake_folder, build_dir, run_cmake_dir, cmake_flags, app_flags, app_data_files)

        self.perform_replay()
        print("DONE")

    def perform_folder_setup(self, cmakelist_dir):
        timestamp_str = generate_timestamp_str()

        run_cmake_dir=os.path.abspath(os.path.join(cmakelist_dir, '..'))
        self.extractor_work_dir=os.path.join(run_cmake_dir, 'extractor_work')
        self.extractor_work_dir=os.path.join(self.extractor_work_dir, self.binary, timestamp_str)

        if self.clean:
            shutil.rmtree(self.extractor_work_dir, ignore_errors=True)
        os.makedirs(self.extractor_work_dir, exist_ok=True)
        return timestamp_str,run_cmake_dir

    # Build app
    # Change original CMakeLists.txt to include extractor code building script if not done before
    def perform_app_build(self, cmakelist_dir, cmake_flags, run_cmake_dir):
        build_dir = ensure_dir_exists(self.extractor_work_dir, 'build')
        locator_out_file = os.path.join(build_dir,'bottom_cmake_folder.txt')
        name_map = {'locator_out_file':locator_out_file, 'binary': self.binary}
        update_app_cmakelists_file(cmakelist_dir, name_map, added_cmakelists_txt = 'CMakeLists.locator.txt',
                                   in_template='CMakeLists.locator.template')
        if self.build_app:
            shutil.rmtree(build_dir, ignore_errors=True)
            #run_cmake3(binary, src_dir, build_dir, run_cmake_dir, cmake_flags) 
            run_cmake(cmakelist_dir, build_dir, run_cmake_dir, cmake_flags, self.binary)
        bottom_cmake_folder = open(locator_out_file, "r").read()
        return build_dir, bottom_cmake_folder


    def perform_codelet_extraction(self, build_dir, profile_df, idx, prefix,  main_src_info):
        mode = self.mode
        COVERAGE = .8

        self.loop_extractor_data_dir = ensure_dir_exists(self.extractor_work_dir, 'LoopExtractor_data')
        top_row = profile_df.iloc[idx]
        #full_source_path = top_row['source_full_path']
        source_location = top_row['source_location']
        compilation_flags = top_row['compilation_flags']
        source_line = int(top_row['line'])

        #source_file = os.path.join(src_dir, source_path)
        nullMask = profile_df['source_full_path'].isnull() | profile_df['line'].isnull()
        profile_df = profile_df[~nullMask]
        profile_df = profile_df[['source_full_path','line','self_time']].groupby(['source_full_path', 'line'],as_index=False).sum()
        profile_df = profile_df.sort_values(by='self_time', ascending=False)

        # Exclude some rows
        if False:
            profile_df = profile_df[~profile_df['source_location'].str.startswith('analyse.c')]
            profile_df = profile_df[~profile_df['source_location'].str.startswith('pixel.c')]
            profile_df = profile_df[~profile_df['source_location'].str.startswith('macroblock.c')]
            profile_df = profile_df[~profile_df['source_location'].str.startswith('me.c')]
        #profile_df = profile_df[~profile_df['source_location'].str.startswith('ratecontrol.c')]

        cumsum = profile_df['self_time'].cumsum()
        covMask = cumsum > profile_df['self_time'].sum() * COVERAGE
        firstIdx = covMask.idxmax()
        # Getting the first rows not exceeding coverage yet
        profile_df = profile_df[:firstIdx+1]

        generateLoopLocFileMulti(profile_df['source_full_path'], 
                                profile_df['line'].astype(int), 
                                profile_df['line'].astype(int), self.loop_extractor_data_dir)
        #generateLoopLocFileMulti([full_source_path], [source_line], [source_line], loop_extractor_data_dir)
        #generateLoopLocFile(full_source_path, source_line, source_line, loop_extractor_data_dir)
        main_src_info = main_src_info.split(':')
        main_source_file = main_src_info[0]

        #sources = sorted({full_source_path, main_source_file})
        sources = sorted(set(profile_df['source_full_path']).union({ main_source_file }))

        source_row_list = []
        for full_source_path in sources:
            try:
                source_row_list += self.run_extractor(build_dir, self.extractor_work_dir, self.loop_extractor_data_dir, prefix, full_source_path, mode)
            except:
                # Do nothing.  Just try next one
                pass
        self.extracted_sources = pd.DataFrame(source_row_list, columns=['orig_src', 'base_src', 'loop_src', 'replay_src', 'global_vars'])
        self.extracted_sources.to_csv(os.path.join(self.loop_extractor_data_dir, 'extracted_sources.csv'), index=False)

    def build_source_row_list(self, source_row_list, full_source_path, bf, lf, rf, glb_vars):
        row_dict = {'orig_src':full_source_path, 'base_src': bf, 
                                    'loop_src': lf, 'replay_src': rf, 'global_vars':glb_vars}
        source_row_list.append(row_dict)

        #name_map, loop_file, util_h_file, util_c_file, segment_info, save_data_dir, save_pointers_h_file, defs_h_file = capture_data(binary, src_dir, build_dir, run_cmake_dir, extractor_work_dir, loop_extractor_data_dir, cmake_flags, app_flags, app_data_file, full_source_path, source_path, extracted_sources)

    def perform_insitu_steps(self, src_dir, bottom_cmake_folder, build_dir, run_cmake_dir, cmake_flags, app_flags, app_data_files):
        cmake_extractor_src_dir = ensure_dir_exists(bottom_cmake_folder, 'extractor_src')
        cmake_extractor_include_dir = ensure_dir_exists(bottom_cmake_folder, 'extractor_include')

        # Will use extracted_sources
        def collect_src_for_folder(folder):
            selected_rows = self.extracted_sources[self.extracted_sources['orig_src'].apply(lambda x: os.path.dirname(x) == folder)]
            return [f for f in selected_rows['loop_src'] if f] + [f for f in selected_rows['base_src'] if f] 


        # name_map = { "loop_src" : loopfilename, "binary" : binary, 
        #             "base_src": basefilename, "orig_src_path": full_source_path, 
        #             "orig_src_folder": os.path.dirname(source_path)}
        # Need to replace original sources ('orig_src' column) by their base ('base_src')
        # and loop ('loop_src') source code.  Need to make sure base and loop source
        # has original source folder in their include path
        orig_src_folders = sorted({os.path.dirname(s) for s in self.extracted_sources['orig_src']})
        src_for_folder_dict = {folder : collect_src_for_folder(folder) for folder in orig_src_folders}
        
        trace_binary=f'trace_{self.binary}'
        extra_libs = self.insitu_libs 

        name_map = { "orig_src_files" : self.extracted_sources['orig_src'],
                    "orig_src_folders" : orig_src_folders,
                    "srcs_for_folder": src_for_folder_dict,
                    "binary": self.binary, "trace_binary": trace_binary, "extra_libs": extra_libs }
        update_app_cmakelists_file(bottom_cmake_folder, name_map, added_cmakelists_txt = 'CMakeLists.extractor.txt',
                                   in_template='CMakeLists.extractor.template')

        #trace_src_file = single_glob(f'{extractor_codelet_src_dir}/trace_*')
        for file in list(self.extracted_sources['loop_src']) + list(self.extracted_sources['base_src']):
            if file: 
                full_file_path = os.path.join(self.loop_extractor_data_dir, file)
                shutil.copy2(full_file_path, cmake_extractor_src_dir)
                
        #initiateConfig(cmake_extractor_include_dir)

        self.copy_extra_insitu_headers(cmake_extractor_include_dir)

        run_cmake(src_dir, build_dir, run_cmake_dir, f'-DBUILD_TRACE_{trace_binary}=ON {cmake_flags}', trace_binary)

        self.run_insitu_binary(build_dir, app_flags, trace_binary, app_data_files)
        print('Finished capture run')

    def copy_extra_insitu_headers(self, cmake_extractor_include_dir):
        pass

    def run_insitu_binary(self, build_dir, app_flags, trace_binary, app_data_files):
        tracer_dir = ensure_dir_exists(self.extractor_work_dir, 'tracer_data')
        self.tracer_run_dir = ensure_dir_exists(tracer_dir, 'run')
        link_app_data_files(self.tracer_run_dir, app_data_files)

        #self.full_trace_binary = os.path.join(build_dir, trace_binary)
        self.full_trace_path = self.find_binary(build_dir, trace_binary)
        self.symlink_trace_binary(self.tracer_run_dir)
        self.run_trace_binary(app_flags)

    @abstractmethod
    def run_trace_binary(self, app_flags):
        pass

    def perform_profile_step(self, app_data_files, app_flags, timestamp_str, build_dir):
        profile_data_dir = ensure_dir_exists(self.extractor_work_dir, 'profile_data')
        self.full_binary_path = self.find_binary(build_dir, self.binary)
        #full_binary_path = os.path.join(build_dir, binary)
        #shutil.copy2(full_binary_path, profile_data_dir)
        self.symlink_orig_binary(profile_data_dir)
        link_app_data_files(profile_data_dir, app_data_files)
        #shutil.copy2(app_data_file, profile_data_dir)
        adv_proj_dir = os.path.join(profile_data_dir, f'proj_{timestamp_str}')

        main_src_file_info, _ = runCmdGetRst(f'nm -a {self.binary} | grep " main$" | cut -d " " -f 1 | xargs addr2line -e {self.binary}', cwd=profile_data_dir)
        #app_cmd = f'./{binary}'
        app_cmd = f'./{self.binary}{app_flags}'
        profile_csv = os.path.join(profile_data_dir, 'profile.csv')
        self.run_advisor(profile_data_dir, adv_proj_dir, app_cmd, profile_csv)
        profile_df = pd.read_csv(profile_csv, skiprows=1, delimiter=',')
        # Select loops only
        loop_profile_df = profile_df[profile_df['function_instance_type'] == 2]
        loop_profile_df = loop_profile_df.sort_values(by='self_time', ascending=False)
        return main_src_file_info,loop_profile_df

    def find_binary(self, build_dir, binary):
        for r, d, fs in os.walk(build_dir):
            if binary in fs:
                return os.path.join(r, binary)
                break
        return None

    def run_advisor(self, advisor_run_dir, adv_proj_dir, app_cmd, profile_csv, use_mockup=True):
        #mockup_profile_csv = '/host/localdisk/cwong29/working/codelet_extractor_work/SPEC2017/extractor_work/525.x264_r/168-238-9156/profile_data/profile.csv'
        mockup_profile_csvs = {'./clover_leaf': '/host/localdisk/cwong29/working/codelet_extractor_work/extractor_work/mockups/profile-clover_leaf.csv', 
                            './525.x264_r --dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720': '/host/localdisk/cwong29/working/codelet_extractor_work/extractor_work/mockups/profile-525.csv',
                            './538.imagick_r -limit disk 0 train_input.tga -resize 320x240 -shear 31 -edge 140 -negate -flop -resize 900x900 -edge 10 train_output.tga': '/host/localdisk/cwong29/working/codelet_extractor_work/extractor_work/mockups/profile-538.csv',
                            './bt.c_compute_rhs_line1892_0':'/host/localdisk/cwong29/working/codelet_extractor_work/extractor_work/mockups/profile-bt.csv'}
        #mockup_profile_csvs = {}
        adv_env = load_advisor_env()
        mockup_profile_csv = mockup_profile_csvs[app_cmd] if app_cmd in mockup_profile_csvs else None
        if not mockup_profile_csv or not use_mockup:
            runCmd(f'advixe-cl --collect survey --project-dir {adv_proj_dir} -- {app_cmd}', 
            cwd=advisor_run_dir, env=adv_env, verbose=True)
            runCmd(f'advisor --report joined --project-dir={adv_proj_dir} > {profile_csv}',
            cwd=advisor_run_dir, env=adv_env, verbose=True)
        else:
            # mockup csv found and use_mockup
            shutil.copy2(mockup_profile_csv, profile_csv)

    def run_extractor(self,build_dir, extractor_work_dir, loop_extractor_data_dir, prefix, full_source_path, mode):
        src_folder=os.path.dirname(full_source_path)
        compile_command_json_file = os.path.join(build_dir, 'compile_commands.json')
        with open(compile_command_json_file, 'r') as f:
            for compile_command in json.load(f):
                cnt_file = compile_command['file']
                #print(cnt_file)
                if os.path.samefile(cnt_file, full_source_path):
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
                        compiler_full_paths = [shutil.which("icx"), shutil.which("icpx")]
                        command_parts = [LOOP_EXTRACTOR_PATH if x in compiler_full_paths else x for x in command_parts]
                    loop_extractor_command = " ".join(command_parts + \
                        ['--extractwd', extractor_work_dir, '--extractsrcprefix', prefix, '--extractmode', mode])
                    break
            else:
                # Not found any build command for this source
                raise Exception("Command not found")
                        
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
        basefilename, loopfilenames, restore_src_files = getLoopFileNames(os.path.join(loop_extractor_data_dir, 'loopFileNames.txt'))
        # Cases:
        # base filename , no loop or restore (for main function and invivo)
        # base filename, loop, no restore (for insitu)
        # base filename, loop, restore (invitro)
        source_row_list = []
        if loopfilenames:
            for lf in loopfilenames:
                rf = f'replay_{lf}'
                rf = rf if rf in restore_src_files else None
                gvs = self.read_globalvar_names(loop_extractor_data_dir, lf)
                self.build_source_row_list(source_row_list, full_source_path, basefilename, lf, rf, gvs)
        else:
            self.build_source_row_list(source_row_list, full_source_path, basefilename, None, None, None)
        return source_row_list

    def read_globalvar_names(self, loop_extractor_data_dir, loopfilename):
        with open(os.path.join(loop_extractor_data_dir, f'globalVarNames_{loopfilename}.txt')) as gf:
            lines = gf.readlines()
            global_vars = [l.replace('"','').strip('\n') for l in lines ]
        return global_vars

    def symlink_orig_binary(self, run_dir):
        self.symlink_binary(run_dir, self.full_binary_path)

    def symlink_trace_binary(self, run_dir):
        self.symlink_binary(run_dir, self.full_trace_path)

    def symlink_binary(self, run_dir, binary):
        os.symlink(binary, os.path.join(run_dir, os.path.basename(binary)))
        


class NonreplayExtraction(Extraction):
    def __init__(self, binary, clean, build_app):
        super().__init__(binary, clean, build_app)

    def run_trace_binary(self, app_flags):
        self.symlink_orig_binary(self.tracer_run_dir)

        
        # print('Running Advisor for original binary')
        # self.run_advisor_nonreplay(self.full_binary_path, app_flags, 'orig_profile.csv')
        # print('Running Advisor for changed binary')
        # self.run_advisor_nonreplay(self.full_trace_binary, app_flags, 'trace_profile.csv')

        print('Running OV for changed binary')
        trace_xp_dir = self.run_oneview(app_flags, self.full_trace_path, 'trace_xp')
        print('Running OV for original binary')
        orig_xp_dir = self.run_oneview(app_flags, self.full_binary_path, 'orig_xp')

        cmp_xp_dir=os.path.join(self.tracer_run_dir, 'cmp_orig_trace')
        run_oneview_cmp(trace_xp_dir, orig_xp_dir, cmp_xp_dir, cwd=self.tracer_run_dir)

        print()
        print(f'Non-replay run at: {self.tracer_run_dir}')

    def run_advisor_nonreplay(self, full_binary, app_flags, out_csv_name):
        trace_profile_csv = os.path.join(self.tracer_run_dir, out_csv_name)        
        trace_adv_proj_dir = os.path.join(self.tracer_run_dir, 'proj_trace')
        trace_binary = os.path.basename(full_binary)
        run_trace_binary = f'./{trace_binary}{app_flags}'
        print(f'Running Advisor for (CMD:{run_trace_binary}) under directory ({self.tracer_run_dir})')
        self.run_advisor(self.tracer_run_dir, trace_adv_proj_dir, run_trace_binary, trace_profile_csv, False)

    def run_oneview(self, app_flags, full_binary, xp_name):
        trace_binary = os.path.basename(full_binary)
        run_trace_binary = f'./{trace_binary}{app_flags}'
        trace_xp_dir=os.path.join(self.tracer_run_dir, xp_name)
        print(f'Running OV for (CMD:{run_trace_binary}) under directory ({self.tracer_run_dir}) with xpdir={trace_xp_dir}')
        run_oneview(run_trace_binary, cwd=self.tracer_run_dir, xp_dir=trace_xp_dir)
        return trace_xp_dir

    @property
    def insitu_libs(self):
        return ""

class InvivoExtraction(NonreplayExtraction):
    def __init__(self, binary, clean, build_app):
        super().__init__(binary, clean, build_app)

    @property
    def mode(self):
        return "invivo"


class InsituExtraction(NonreplayExtraction):
    def __init__(self, binary, clean, build_app):
        super().__init__(binary, clean, build_app)

    @property
    def mode(self):
        return "insitu"

class InvitroExtraction(Extraction):
    def __init__(self, binary, clean, build_app):
        super().__init__(binary, clean, build_app)

    @property
    def mode(self):
        return "invitro"

    @property
    def insitu_libs(self):
        return "cere_dump"

    def copy_extra_insitu_headers(self, cmake_extractor_include_dir):
        self.cere_src_folder = os.path.join(SCRIPT_DIR, 'src', 'cere')
        tracee_h_file = os.path.join(self.cere_src_folder, 'tracee.h')
        shutil.copy2(tracee_h_file, cmake_extractor_include_dir)

        types_h_file = os.path.join(self.cere_src_folder, 'types.h')
        shutil.copy2(types_h_file, cmake_extractor_include_dir)
    
    def run_trace_binary(self, app_flags):
        trace_binary = os.path.basename(self.full_trace_path)
        run_trace_binary = f'./{trace_binary}{app_flags}'
        runCmd(run_trace_binary, cwd=self.tracer_run_dir, verbose=True)

    def perform_replay(self):
        self.cere_out_dir = os.path.join(self.tracer_run_dir, ".cere")
        run_replay_steps(self.binary, self.extractor_work_dir, self.loop_extractor_data_dir, self.extracted_sources, self.cere_src_folder, self.cere_out_dir, self.full_trace_path)
        print('Finished replay runs')


def main():
    arg_parser = argparse.ArgumentParser(description="Codelet Extractor for different purposes.")
    arg_parser.add_argument('--mode', default='invitro', choices=['invitro', 'insitu', 'invivo'], help='invitro extraction, insitu extraction, or invivo codelet marking')
    args = arg_parser.parse_args()


    clean = True
    build_app=True

    # TODO: mark these command line arguments
    binary='525.x264_r'
    if False:
        binary='538.imagick_r'
        binary='519.lbm_r'
        binary='531.deepsjeng_r'
        binary='500.perlbench_r'
        binary='502.gcc_r'
        binary='520.omnetpp_r'
        binary='557.xz_r'
    binary='508.namd_r'
    binary='511.povray_r'
    binary='507.cactuBSSN_r'
    binary='510.parest_r'
    binary='554.roms_r'
    binary='526.blender_r'
    binary='549.fotonik3d_r'
    binary='531.deepsjeng_r'
    binary='500.perlbench_r'
    binary='502.gcc_r'
    binary='544.nab_r'
    binary='505.mcf_r'
    binary='520.omnetpp_r'
    binary='523.xalancbmk_r'
    binary='541.leela_r'
    #binary='clover_leaf'
    #binary='bt.c_compute_rhs_line1892_0'
    # TODO: for SPEC, do "grep workload 1 result/*.log file multi workload situation"
    if binary == '525.x264_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['BuckBunny.yuv'], is_int=True)
        app_flags = ' --dumpyuv 50 --frames 156 -o BuckBunny_New.264 BuckBunny.yuv 1280x720'
    elif binary == '538.imagick_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['train_input.tga'], is_int=False)
        app_flags = ' -limit disk 0 train_input.tga -resize 320x240 -shear 31 -edge 140 -negate -flop -resize 900x900 -edge 10 train_output.tga'
    elif binary == '519.lbm_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['100_100_130_cf_b.of'], is_int=False)
        app_flags = ' 300 reference.dat 0 1 100_100_130_cf_b.of'
    elif binary == '531.deepsjeng_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['train.txt'], is_int=True)
        app_flags = ' train.txt'
    elif binary == '500.perlbench_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['lib', 'diffmail.pl'], is_int=True)
        app_flags = ' -I./lib diffmail.pl 2 550 15 24 23 100'
    elif binary == '502.gcc_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['200.c'], is_int=True)
        app_flags = ' 200.c -O3 -finline-limit=50000 -o 200.opts-O3_-finline-limit_50000.s'
    elif binary == '505.mcf_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['inp.in'], is_int=True)
        app_flags = ' inp.in'
    elif binary == '520.omnetpp_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['ned', 'omnetpp.ini'], is_int=True)
        app_flags = ' -c General -r 0'
    elif binary == '523.xalancbmk_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['allbooks.xml', 'xalanc.xsl'], is_int=True)
        app_flags = ' -v allbooks.xml xalanc.xsl'
    elif binary == '541.leela_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['train.sgf'], is_int=True)
        app_flags = ' train.sgf'
    elif binary == '557.xz_r':
        # Multi run picked one
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['input.combined.xz'], is_int=True)
        app_flags = ' input.combined.xz 40 a841f68f38572a49d86226b7ff5baeb31bd19dc637a922a972b2e6d1257a890f6a544ecab967c313e370478c74f760eb229d4eef8a8d2836d233d3e9dd1430bf 6356684 -1 8'
    elif binary =='503.bwaves_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['bwaves_1.in'], is_int=False)
        # Segfault in original run , fortran
        app_flags = ' bwaves_1 < bwaves_1.in'
    elif binary =='508.namd_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['apoa1.input'], is_int=False)
        app_flags = ' --input apoa1.input --iterations 7 --output apoa1.train.output'
    elif binary =='511.povray_r':
        cmakelist_dir, cmake_flags, app_data_files = \
            get_spec_cmake_flags(binary, ['SPEC-benchmark-train.ini','SPEC-benchmark-train.pov','SPEC-benchmark.tga','arrays.inc',
                                          'chars.inc','colors.inc','consts.inc','debug.inc','finish.inc','functions.inc','glass.inc',
                                          'glass_old.inc','golds.inc','logo.inc','math.inc','metals.inc','rad_def.inc','rand.inc',
                                          'screen.inc','shapes.inc','shapes2.inc','shapes_old.inc','shapesq.inc','skies.inc',
                                          'stage1.inc','stars.inc','stdcam.inc','stdinc.inc','stoneold.inc','stones.inc','stones1.inc',
                                          'stones2.inc','strings.inc','sunpos.inc','textures.inc','transforms.inc','woodmaps.inc',
                                          'woods.inc'], is_int=False)
        app_flags = ' SPEC-benchmark-train.ini'
    elif binary =='521.wrf_r':
        cmakelist_dir, cmake_flags, app_data_files = \
            get_spec_cmake_flags(binary, ['GENPARM.TBL','LANDUSE.TBL','RRTM_DATA','SOILPARM.TBL','VEGPARM.TBL','namelist.input',
                                          'wrfbdy_d01','wrfinput_d01'], is_int=False)
        # Segfault in original run , fortran
        app_flags = ''
    elif binary =='527.cam4_r':
        cmakelist_dir, cmake_flags, app_data_files = \
            get_spec_cmake_flags(binary, ['USGS-gtopo30_1.9x2.5_remap_c050602.nc','dust2_camrt_c080918.nc',
                                          'abs_ems_factors_fastvx.c030508.nc','dust3_camrt_c080918.nc',
                                          'aero_1.9x2.5_L26_2000clim_c091112.nc','dust4_camrt_c080918.nc','atm_in',
                                          'ocphi_camrt_c080918.nc','bcphi_camrt_c080918.nc','ocpho_camrt_c080918.nc',
                                          'bcpho_camrt_c080918.nc','ozone_1.9x2.5_L26_2000clim_c091112.nc',
                                          'cami_0000-01-01_1.9x2.5_L26_APE_c080203.nc','ssam_camrt_c080918.nc','clim_p_trop.nc',
                                          'sscm_camrt_c080918.nc','drv_in','sulfate_camrt_c080918.nc','dust1_camrt_c080918.nc'], 
                                 is_int=False)
        # Segfault in original run, fortran
        app_flags = ''
    elif binary =='544.nab_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['aminos'], is_int=False)
        app_flags = ' aminos 391519156 1000'
    elif binary =='554.roms_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['ocean_benchmark1.in.x', 'varinfo.dat'], is_int=False)
        app_flags = ' < ocean_benchmark1.in.x'
    elif binary =='507.cactuBSSN_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['spec_train.par'], is_int=False)
        app_flags = ' spec_train.par'
    elif binary =='510.parest_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['train.prm'], is_int=False)
        app_flags = ' train.prm'
    elif binary =='526.blender_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['sh5_reduced.blend'], is_int=False)
        app_flags = ' sh5_reduced.blend --render-output sh5_reduced_ --threads 1 -b -F RAWTGA -s 234 -e 234 -a'
    elif binary =='549.fotonik3d_r':
        cmakelist_dir, cmake_flags, app_data_files = get_spec_cmake_flags(binary, ['OBJ.dat','PSI.dat','TEwaveguide.m', 
                                                                                   'incident_W3PC.def','power1.dat','yee.dat'], 
                                                                          is_int=False)
        app_flags = ''
    elif binary == 'clover_leaf':
        cmakelist_dir=os.path.join(PREFIX,'CloverLeaf')
        cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-DUSE_OPENMP"'
        cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-DUSE_OPENMP -g" -DCMAKE_C_FLAGS="-g"'
        cmake_flags = '-DCMAKE_CXX_COMPILER=mpiicpc -DCMAKE_CXX_FLAGS="-cxx=icpx -DUSE_OPENMP -g" -DCMAKE_C_FLAGS="-g"'

        app_data_files = os.path.join(cmakelist_dir, 'clover.in')

        app_flags = ''
    elif binary == 'bt.c_compute_rhs_line1892_0':
        cmakelist_dir=os.path.join(PREFIX,'qaas-demo-lore-codelets')
        cmake_flags = f'-DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g"'
        app_data_files = os.path.join(cmakelist_dir, 'src','all','NPB_2.3-OpenACC-C','BT','bt.c_compute_rhs_line1892_0','codelet.data')
        app_flags = ''
    else:
        return

    top_n = 21
    top_n = 2
    top_n = 1
    if args.mode == 'invitro':
        extraction = InvitroExtraction(binary, clean, build_app)
    elif args.mode == 'insitu':
        extraction = InsituExtraction(binary, clean, build_app)
    elif args.mode == 'invivo':
        extraction = InvivoExtraction(binary, clean, build_app)
    else:
        raise Exception('Unknown Extraction type:'+args.mode)
    extraction.perform_extraction_steps(top_n, cmakelist_dir, cmake_flags, app_data_files, app_flags)

def get_spec_cmake_flags(binary, datafile_names, is_int):
    cmakelist_dir=os.path.join(PREFIX, 'SPEC2017/llvm-test-suite')
    app_prefix=os.path.join(PREFIX, f'SPEC2017/benchmark/benchspec/CPU/{binary}/run/run_base_train_myTest.0000')
    app_data_files=[os.path.join(app_prefix, f) for f in datafile_names]
    if is_int:
        SPEC_CFLAGS = "-g -xCORE-AVX512 -mfpmath=sse -O3 -ffast-math -funroll-loops -flto -qopt-mem-layout-trans=4"
        TEST_SUITE_SUBDIRS = "External/SPEC/CINT2017rate"
    else: 
        SPEC_CFLAGS = "-g -xCORE-AVX512 -mfpmath=sse -Ofast -ffast-math -funroll-loops -flto -qopt-mem-layout-trans=4"
        TEST_SUITE_SUBDIRS = "External/SPEC/CFP2017rate"
    SPEC_LINKER_FLAGS="-flto"
    spec_src_dir=os.path.join(PREFIX, 'SPEC2017/benchmark')
    return cmakelist_dir, f'-DTEST_SUITE_SUBDIRS={TEST_SUITE_SUBDIRS} -DTEST_SUITE_SPEC2017_ROOT={spec_src_dir} -DCMAKE_C_COMPILER=icx -DCMAKE_CXX_COMPILER=icpx \
            -DCMAKE_C_FLAGS="{SPEC_CFLAGS}" -DCMAKE_CXX_FLAGS="{SPEC_CFLAGS}" -DCMAKE_EXE_LINKER_FLAGS="{SPEC_LINKER_FLAGS}" -DTEST_SUITE_COLLECT_CODE_SIZE=OFF', app_data_files



def run_oneview(myCmd, cwd, xp_dir, env=os.environ.copy()):
    oneviewCmd = f'{OV_PATH} oneview -R1 -xp={xp_dir} -- {myCmd}'
    runCmd(oneviewCmd, cwd, env)
def run_oneview_cmp(xp1, xp2, xp_out, cwd, env=os.environ.copy()):
    oneviewCmd = f'{OV_PATH} oneview --compare-reports --inputs={xp1},{xp2} -xp={xp_out}'
    runCmd(oneviewCmd, cwd, env)

def link_app_data_files(profile_data_dir, app_data_files):
    for app_data_file in app_data_files:
        os.symlink(app_data_file, os.path.join(profile_data_dir, os.path.basename(app_data_file)))


def run_replay_steps(binary, extractor_work_dir, loop_extractor_data_dir, extracted_sources, cere_src_folder, cere_out_dir, full_trace_binary):
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
                addrs = [os.path.splitext(os.path.basename(f))[0] for f in glob(f'{cere_dump_dir}/*.memdump')]
                # Sort according to their hex values
                addrs.sort(key=lambda h:int(h,16))
                for addr in addrs:
                #for memdump_file in glob(f'{cere_dump_dir}/*.memdump'):
                    memdump_file = f'{cere_dump_dir}/{addr}.memdump'
                    shutil.copy2(memdump_file, restore_data_dir)
                    # Drop prefix directory name and also extension
                    base_memdump_file = os.path.basename(memdump_file)
                    #addr = os.path.splitext(base_memdump_file)[0]
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
        #restore_cmake_flags = f'-DCMAKE_C_COMPILER=icc -DCMAKE_CXX_COMPILER=icpc -DCMAKE_CXX_FLAGS="-g -D__RESTORE_CODELET__" -DCMAKE_C_FLAGS="-g -D__RESTORE_CODELET__"'
        #restore_cmake_flags = f'-DCMAKE_C_COMPILER=clang-7 -DCMAKE_CXX_COMPILER=clang++-7 -DCMAKE_CXX_FLAGS="-g -D__RESTORE_CODELET__" -DCMAKE_C_FLAGS="-g -D__RESTORE_CODELET__"'
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



def run_cmake(cmakelist_dir, build_dir, run_cmake_dir, cmake_flags, trace_binary):
    runCmd(f'cmake {cmake_flags} -DCMAKE_EXPORT_COMPILE_COMMANDS=1 -S {cmakelist_dir} -B {build_dir}', 
           cwd=run_cmake_dir, verbose=True, throwException=True)
    runCmd(f'cmake --build {build_dir} --target {trace_binary}', cwd=run_cmake_dir, verbose=True,
           throwException=True)

def update_app_cmakelists_file(src_dir, name_map, added_cmakelists_txt, in_template):
    orig_cmakelist_txt_file = os.path.join(src_dir, 'CMakeLists.txt')
    include_extractor_build_line = f"include({added_cmakelists_txt})"
    with open(orig_cmakelist_txt_file, 'r+') as file:
        for line in file:
            if include_extractor_build_line in line:
                break
        else:
            # The line to include extra build code is not in so add one
            file.write(include_extractor_build_line)

    instantiate_cmakelists_file(name_map, in_template = in_template, 
                                out_instantiated_file=os.path.join(src_dir, added_cmakelists_txt))

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
