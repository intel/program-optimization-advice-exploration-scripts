# Contributors: Padua/Yoonseo
import argparse
import datetime
import json
import os
import shutil
import subprocess

import icelib.tools.search.resultsdb.models as m
from Cheetah.Template import Template

from app_builder import build_argparser as builder_build_argparser
from app_builder import build_binary, get_build_dir, setup_build
from app_runner import build_argparser as runner_build_argparser
from app_runner import AppRunner
from logger import QaasComponents, log
from utils.util import generate_timestamp_str
from utils.util import parse_env_map 
from fdo_lib import LocusRunner
from fdo_lib import LProfProfiler
from fdo_lib import LocusDbAccess

script_dir=os.path.dirname(os.path.realpath(__file__))
template_dir=os.path.join(script_dir, '..', 'templates')
tmp_dir="/nfs/site/proj/alac/tmp/qaas-locus-runs"
tmp_dir="/tmp/qaas-locus-runs"


# def instantiate_template(template_file, names, out_dir, outfile_name):
#     scop_template = Template.compile(file=os.path.join(template_dir, template_file))
#     scop_def = scop_template(searchList=[names])
#     full_filename=os.path.join(out_dir, outfile_name)
#     print(scop_def, file=open(full_filename, 'w'))
#     return full_filename

#def generate_locus_file_and_scripts(dbfile, run_dir, compiler, src_file, codelet_name, locus_bin_run_dir, inc_flags):
#    iceorig_file, locus_outfile_suffix, build_cmd_sh_file, timing_script_file, timing_fn_name = generate_build_run_timing_scripts(run_dir, src_file, codelet_name, locus_bin_run_dir)
#
#    locus_file, preproc_folders, locus_run_cmd = generate_locus_command(dbfile, src_file, codelet_name, inc_flags, locus_outfile_suffix, timing_script_file, timing_fn_name)
#                    
#    # returning iceorig_file to be restored by build_cmd script after each Locus search step
#    # Also return locus_run_cmd to be used
#    return iceorig_file, locus_run_cmd, dbfile, locus_file, preproc_folders, build_cmd_sh_file

# def generate_locus_command(dbfile, src_file, inc_flags, locus_outfile_suffix, timing_script_file, timing_fn_name, ntests):
#     # Locus will invoke build_cmd script and that script will make use of full_iceorig_file to restore back to full_src_file
#     #engine='exhaustive'
#     preproc_folders = [part.strip() for part in inc_flags.split("-I") if part]

#     locus_run_cmd, locus_file = generate_locus_run_cmd(dbfile, src_file, 'qaas', locus_outfile_suffix, timing_fn_name, timing_script_file, ntests, preproc_folders)
                    
#     return locus_file,preproc_folders,locus_run_cmd


# def generate_build_script(run_dir, src_file, codelet_name, make_cmd, names):
#     #src_file='bt.c_compute_rhs_line1892_loop.c'
#     #src_file='bt.c_compute_rhs_line1907_loop.c'
#     exe_file=codelet_name

#     iceorig_file, locus_outfile_suffix, build_cmd_sh_file = \
#         generate_build_cmd_sh(names, run_dir, src_file, make_cmd, exe_file)
#     return iceorig_file, locus_outfile_suffix, build_cmd_sh_file, names


# def generate_run_script(run_dir):

#     run_cmd=f'python {script_dir}/app_runner.py' \
# 		+ f" --binary-path $QAAS_binary_path" \
# 		+ f" --run-dir $QAAS_run_dir" \
# 		+ f" --data-path $QAAS_data_path" \
# 		+ f" --mode run" \
# 		+ f" --run-cmd \"$QAAS_run_cmd\""

#     run_cmd_sh_file, names = generate_run_cmd_sh(run_dir, run_cmd)
#     return run_cmd_sh_file,names


def generate_build_cmd():
    make_cmd=f'python {script_dir}/app_builder.py' \
        + f" --src-dir \"$QAAS_locus_src_dir\"" \
		+ " --mode make " \
		+ f" --output-binary-path \"$QAAS_binary_path\"" \
		+ f" --compiler-dir \"$QAAS_compiler_dir\"" \
		+ f" --orig-user-CC \"$QAAS_orig_user_CC\"" \
		+ f" --target-CC \"$QAAS_user_CC\"" \
		+ f" --user-c-flags=\"$QAAS_user_c_flags\"" \
		+ f" --user-cxx-flags=\"$QAAS_user_cxx_flags\"" \
		+ f" --user-fc-flags=\"$QAAS_user_fc_flags\"" \
		+ f" --user-link-flags=\"$QAAS_user_link_flags\"" \
		+ f" --user-target \"$QAAS_user_target\"" \
		+ f" --user-target-location \"$QAAS_user_target_location\""
    return make_cmd

# def generate_locus_scripts(run_dir, names, build_cmd_sh_file, 
#                            run_cmd_sh_file, insert_pragma_before_line,
#                            locus_bin, locus_bin_run_dir):
#     new_loop_head_line_num = insert_pragma_before_line + 1
#     names.update({
#         "timing_script_loop_head": new_loop_head_line_num,
#         "locus_bin": locus_bin,
#         'locus_run_dir': run_dir,
#         "locus_bin_run_dir": locus_bin_run_dir
#     })
#     timing_fn_name='getTimingQaas' 
#     timing_script_file = generate_timing_and_locus_scripts(names, run_dir, build_cmd_sh_file, run_cmd_sh_file, timing_fn_name)
#     return timing_script_file, timing_fn_name

# Execution scheme:
# 
# Given original file <file>
# 1. save <file> to <file>.orig to restore at the end
#
# 2. Change, in place, file <file> original pragma to ICE pragma  (<file> now updated to contain ICE pragma)
# 3. Copy <file> to <file>.iceorig
# 3.5 setup build (set up CMake build directory) 
# 4. Invoke Locus with <file> as input and suffix .opt so output <file>.opt
# 5. In build command (NOT IN PYTHON SCRIPT), 
#   a. mv <file>.opt to <file>
#   b. proceed to normal building procedure (so LORE output file will be used)
#   c. cp <file>.iceorig to <file> to restore it for next steps of search
# 6. after all is done
#   mv <file>.orig <file>
def exec(locus_run_root, src_dir, compiler_dir, maqao_path, output_binary_path, orig_user_CC, user_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
         data_path, run_cmd, env_var_map, target_location):
    # Will be created by Locus
    helper = QaaSLocusRunner(locus_run_root, src_dir, compiler_dir, maqao_path, output_binary_path, orig_user_CC, user_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
         data_path, run_cmd, env_var_map, target_location)

    helper.exec_locus()


    if LocusDbAccess(helper.db_file).extract_best_variant(helper.locus_file, helper.locus_result_dir, helper.preproc_folders):
        # Best variant regenerated in place, so rebuild will produce opt executable
        os.remove(helper.locus_bin)
        build_binary(user_target, helper.build_dir, target_location, helper.env, helper.output_dir, helper.output_name)
        # Copy the binary to result directory 
        os.makedirs(os.path.dirname(output_binary_path), exist_ok=True)
        print(f'Copying mutator output binary to {output_binary_path} from {helper.locus_bin}')
        shutil.copy2(helper.locus_bin, output_binary_path)
    return helper.env

# def exec_locus(helper):
#     helper.setup_locus_run_dir()

#     #run_cmd_sh_file, template_names = generate_run_script(run_dir)

#     helper.set_target()

#     iceorig_file, locus_run_cmd = helper.generate_locus_file_and_scripts()

#    run_locus(helper.locus_run_dir, helper.env, helper.full_src_file, iceorig_file, locus_run_cmd, helper)

# def generate_locus_file_and_scripts(helper):
#     run_cmd_sh_file, template_names = generate_run_cmd_sh(helper.run_dir, helper.run_cmd)

#     iceorig_file, locus_outfile_suffix, build_cmd_sh_file = \
#         generate_build_cmd_sh(template_names, helper.run_dir, helper.full_src_file, helper.build_cmd, helper.exe_file)


#     timing_fn_name = helper.finalize_locus_scripts_names(template_names)
#     timing_script_file = generate_timing_and_locus_scripts(template_names, helper.run_dir, build_cmd_sh_file, run_cmd_sh_file, timing_fn_name)
#     # Setup dep file needed for Locus runs
#     helper.setup_dep_files(helper.full_src_file)

#     ntests=500
#     #ntests=50
#     #locus_file, header_folders, locus_run_cmd = generate_locus_command(dbfile, full_src_file, inc_flags, locus_outfile_suffix, timing_script_file, timing_fn_name, ntests)
#     locus_run_cmd = helper.generate_locus_command(helper.db_file, helper.full_src_file, locus_outfile_suffix, timing_script_file, timing_fn_name, ntests)
#     return iceorig_file,locus_run_cmd

def get_target_loop(compiler_dir, maqao_path, orig_user_CC, user_CC, user_c_flags, user_cxx_flags, user_fc_flags, \
    user_link_flags, user_target, data_path, app_run_cmd, target_location, run_dir, locus_src_dir, locus_bin_run_dir, \
        locus_bin, env):
    make_cmd = generate_build_cmd()

    #build_binary(user_target, build_dir, env, output_dir, output_name)
    # See script generation function for the user of these variables
    #make_sh_cmd=f'./{build_cmd_sh_file}'
    make_sh_cmd = make_cmd
    env["QAAS_locus_src_dir"]=f"{locus_src_dir}"
    env["QAAS_binary_path"]=f"{locus_bin}"
    env["QAAS_compiler_dir"]=f"{compiler_dir}"
    env["QAAS_orig_user_CC"]=f"{orig_user_CC}"
    env["QAAS_user_CC"]=f"{user_CC}"
    env["QAAS_user_c_flags"]=f"{user_c_flags}"
    env["QAAS_user_cxx_flags"]=f"{user_cxx_flags}"
    env["QAAS_user_fc_flags"]=f"{user_fc_flags}"
    env["QAAS_user_link_flags"]=f"{user_link_flags}"
    env["QAAS_user_target"]=f"{user_target}"
    env["QAAS_user_target_location"]=f"{target_location}"

    # below command try the make script
    subprocess.run(f'/bin/bash -c \'{make_sh_cmd}\'', shell=True, env=env, cwd=run_dir)
    build_dir = get_build_dir(locus_src_dir)
    compile_command_json_file = os.path.join(build_dir, 'compile_commands.json')

#1.5 setup trial run to select loops (before insert of Locus pragma)
    AppRunner(locus_bin_run_dir, maqao_path).prepare(locus_bin, data_path)

    full_src_file, insert_pragma_before_line = profile_app(run_dir, maqao_path, data_path, app_run_cmd, locus_bin_run_dir, locus_bin, env)
    return make_cmd,build_dir,compile_command_json_file,full_src_file,insert_pragma_before_line

def setup_locus_run_dir(locus_run_root, src_dir, compiler_dir, orig_user_CC, user_CC, user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, env_var_map):
    locus_ts_str = generate_timestamp_str()
    run_dir = os.path.join(locus_run_root, f"run-{locus_ts_str}")

    os.makedirs(run_dir)

    locus_src_dir = os.path.join(run_dir, 'src')
    locus_bin_run_dir = os.path.join(run_dir, 'run')
    locus_bin = os.path.join(locus_bin_run_dir, 'pgm')
    locus_result_dir = os.path.join(run_dir, 'results')

    # copy source tree to run_dir for Locus processing
    shutil.copytree(src_dir, locus_src_dir, symlinks=True)

    
    build_dir, output_dir, output_name, env = setup_build(locus_src_dir, compiler_dir, locus_bin, orig_user_CC, user_CC, 
                                                          user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags)

    env.update(env_var_map)
    return run_dir,locus_src_dir,locus_bin_run_dir,locus_bin,locus_result_dir,output_dir,output_name,env

class QaaSLocusRunner(LocusRunner):
    def __init__(self, locus_run_root, src_dir, compiler_dir, maqao_path, output_binary_path, orig_user_CC, user_CC, 
        user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
        data_path, app_run_cmd, env_var_map, target_location):
        super().__init__()
        self.locus_run_root = locus_run_root
        self.src_file = None

        self.src_dir = src_dir
        self.compiler_dir = compiler_dir
        self.maqao_path = maqao_path
        self.output_binary_path = output_binary_path
        self.orig_user_CC = orig_user_CC
        self.user_CC = user_CC
        self.user_c_flags = user_c_flags
        self.user_cxx_flags = user_cxx_flags
        self.user_fc_flags = user_fc_flags
        self.user_link_flags = user_link_flags
        self.user_target = user_target
        self.data_path = data_path
        self.app_run_cmd = app_run_cmd
        self.env_var_map = env_var_map
        self.target_location = target_location
        self.full_src_file = None

    # This set self.run_dir which implicitly also define self.db_file property
    def setup_locus_run_dir(self):
        self.run_dir, self.locus_src_dir, self.locus_bin_run_dir, self.locus_bin, self.locus_result_dir, self.output_dir, self.output_name, \
            self.env = setup_locus_run_dir(self.locus_run_root, self.src_dir, self.compiler_dir, self.orig_user_CC, self.user_CC, \
                self.user_c_flags, self.user_cxx_flags, self.user_fc_flags, self.user_link_flags, self.env_var_map)


    def insert_locus_pragma(self, full_src_file):
        insert_locus_pragma(full_src_file, self.insert_pragma_before_line)

    def set_locus_env(self, env):
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f'{env["PYTHONPATH"]}:{script_dir}'
        else:
            env['PYTHONPATH'] = script_dir

    # def generate_locus_command(self, dbfile, full_src_file, locus_outfile_suffix, timing_script_file, timing_fn_name, ntests):
    #     # Locus will invoke build_cmd script and that script will make use of full_iceorig_file to restore back to full_src_file
    #     #engine='exhaustive'

    #     locus_run_cmd, self.locus_file = generate_locus_run_cmd(dbfile, full_src_file, self.suffixinfo, locus_outfile_suffix, timing_fn_name, timing_script_file, ntests, self.preproc_folders)
                    
    #     return locus_run_cmd

    def setup_dep_files(self, full_src_file):
        self.inc_flags = setup_dep_files(self.compile_command_json_file, full_src_file)

    def finalize_locus_scripts_names(self, names):
        new_loop_head_line_num = self.insert_pragma_before_line + 1
        names.update({
            "timing_script_loop_head": new_loop_head_line_num,
            "locus_bin": self.locus_bin,
            'locus_run_dir': self.run_dir,
            "locus_bin_run_dir": self.locus_bin_run_dir,
            "maqao_path": self.maqao_path
            })
        timing_fn_name='getTimingQaas' 
        return timing_fn_name

    @property
    def build_cmd(self):
        return self._build_cmd

    @property
    def run_cmd(self):
        return f'python {script_dir}/app_runner.py' \
            + f" --binary-path $QAAS_binary_path" \
            + f" --maqao-path $QAAS_maqao_path" \
                + f" --run-dir $QAAS_run_dir" \
		+ f" --data-path $QAAS_data_path" \
		+ f" --mode run" \
		+ f" --run-cmd \"$QAAS_run_cmd\""

    @property
    def exe_file(self):
        return 'conv'

    def set_target(self):
        if not self.full_src_file:
            self._build_cmd, self.build_dir, self.compile_command_json_file, self.full_src_file, self.insert_pragma_before_line = \
            get_target_loop(self.compiler_dir, self.maqao_path, self.orig_user_CC, self.user_CC, self.user_c_flags, self.user_cxx_flags, self.user_fc_flags, \
                self.user_link_flags, self.user_target, self.data_path, self.app_run_cmd, self.target_location, self.run_dir, \
                    self.locus_src_dir, self.locus_bin_run_dir, \
                    self.locus_bin, self.env)

    # Locus run directory is the run directory
    @property
    def locus_run_dir(self):
        return self.run_dir

    @property
    def preproc_folders(self):
        return [part.strip() for part in self.inc_flags.split("-I") if part]

    # Return the suffix info for Locus runs
    @property
    def suffixinfo(self):
        return 'qaas'
        

# def run_locus(run_dir, env, full_src_file, insert_pragma_before_line, iceorig_file, locus_run_cmd):
#     full_restore_src_file=full_src_file + '.orig'
#     shutil.copy2(full_src_file, full_restore_src_file) # save restore file

# # 2. Add, in place, file <file> ICE pragma  (<file> now updated to contain ICE pragma)
#     insert_locus_pragma(full_src_file, insert_pragma_before_line)
#     # input(f'check file: {full_src_file}')

# # 3. Copy <file> to <file>.iceorig
#     # full_src_file now have ICE pragma instead
#     # save to iceorig file.  Note this file will be used by build_cmd scrpt to restore it after each Locus search step
#     full_iceorig_file=os.path.join(run_dir, iceorig_file)
#     shutil.copy2(full_src_file, full_iceorig_file) 

# # 4. Invoke Locus with <file> as input and suffix .opt so output <file>.opt
# # 5. In build command (NOT IN PYTHON SCRIPT), 
# #   a. mv <file>.opt to <file>
# #   b. proceed to normal building procedure (so LORE output file will be used)
# #   c. cp <file>.iceorig to <file> to restore it for next steps of search
    
#     set_locus_env(env)
#     subprocess.run(locus_run_cmd, shell=True, env=env, cwd=run_dir)

# # 6. after all is done (reverse operation of #1)
# #   mv <file>.orig <file>
#     shutil.copy2(full_restore_src_file, full_src_file)

def profile_app(run_dir, maqao_path, data_path, app_run_cmd, locus_bin_run_dir, locus_bin, env):
    #run_sh_cmd=f'./{run_cmd_sh_file}'
    env["QAAS_run_dir"]=f"{locus_bin_run_dir}"
    env["QAAS_maqao_path"]=f"{maqao_path}"
    env["QAAS_data_path"]=f"{data_path}"
    env["QAAS_run_cmd"]=f"{app_run_cmd}"
    # below command try the run script
    loop_profile_df = LProfProfiler(maqao_path).collect_loop_info(app_run_cmd, locus_bin_run_dir, locus_bin, env)
    # Now pick the hottest loop for tuning
    # TODO: setup with budget in mind to try more loops and/or specific loops
    target_loop_profile_df = loop_profile_df.head(1)
    target_loop_path = target_loop_profile_df['Loop Path'].item()
    target_outter_loop_loc = target_loop_path[0]
    full_src_file, target_line_no = target_outter_loop_loc.split(':')
    insert_pragma_before_line = int(target_line_no)

    print(full_src_file)
    return full_src_file,insert_pragma_before_line


def setup_dep_files(compile_command_json_file, full_src_file):
    src_folder=os.path.dirname(full_src_file)
    with open(compile_command_json_file, 'r') as f:
        for compile_command in json.load(f):
            cnt_file = compile_command['file']
            print(cnt_file)
            if os.path.samefile(cnt_file, full_src_file):
                print('match')
                matched_command = compile_command['command']
                print(matched_command)
                inc_flags = " ".join([part for part in matched_command.split(" ") if part.startswith('-I')]+[f'-I{src_folder}'])
                dep_file=os.path.join(src_folder, os.path.splitext(os.path.basename(full_src_file))[0]+'.dep')
                # Write the inc flags to dep file to be picked up by ROSE
                with open(dep_file, 'w') as f: f.write(inc_flags)
                break
    return inc_flags

# def set_locus_env(env):
#     # Add script directory to ensure getTiming script can use QaaS scripts
#     if 'PYTHONPATH' in env:
#         env['PYTHONPATH'] = f'{env["PYTHONPATH"]}:{script_dir}'
#     else:
#         env['PYTHONPATH'] = script_dir

def insert_locus_pragma(full_src_file, insert_pragma_before_line):
    with open(full_src_file, 'r') as rd:
        lines = rd.readlines()
    with open(full_src_file, 'w') as wr:
        for line_num, line in enumerate(lines):
            if line_num + 1 == insert_pragma_before_line:
                wr.write('#pragma @ICE loop=scop\n')
            wr.write(line)


# # Return True if best variant generated False if not
# def extract_best_variant(db_path, lfname, result_dir, header_folders):
#     debug = False
#     engine, session = connect('sqlite:///'+db_path, debug)
#     variants = (session.query(m.Variant)
#                 .join(m.Search, m.Search.id == m.Variant.searchid)
#                 .join(m.LocusFile)
#                 .filter(m.LocusFile.locusfilename == lfname))
#     min_median = float("inf")
#     min_median_variant = None
#     for var in variants:
#         unit, median_metric = get_median_metric(var)
#         assert unit == LProfProfiler.LPROF_AVG_CYCLES_METRIC
#         if median_metric < min_median:
#             min_median_variant = var
#             min_median = median_metric
#     if min_median_variant:
#         x = session.query(m.Search,m.LocusFile.locusfilename).join(m.LocusFile)
#         # Found the best variant, regenerate source and locus file
#         workdir=os.path.join(result_dir, f'v-{min_median_variant.id}')
#         regenerate(session, x, workdir, int(min_median_variant.id), header_folders)
#         # Note the source code is regenerated in place to replace the source file
#         return True
#     return False

def main():
    parser = argparse.ArgumentParser(description="Run mutator in QaaS")
    # Builder flags
    builder_build_argparser(parser, include_mode=False)

    # runner flags
    runner_build_argparser(parser, include_mode=False)

    parser.add_argument('--locus-run-root', help='Path to root of locus run directory', required=True)
    args = parser.parse_args()
    env_var_map = parse_env_map(args)
    exec(args.locus_run_root, args.src_dir, args.compiler_dir, args.maqao_path, args.output_binary_path, args.orig_user_CC, args.target_CC,
         args.user_c_flags, args.user_cxx_flags, args.user_fc_flags, args.user_link_flags, args.user_target,
         args.data_path, args.run_cmd, env_var_map, args.user_target_location)

if __name__ == "__main__": 
    main()
