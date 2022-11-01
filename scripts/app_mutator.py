# Contributors: Padua/Yoonseo
import argparse
import datetime
import json
import os
import re
import shutil
import stat
import subprocess

import icelib.tools.search.resultsdb.models as m
from Cheetah.Template import Template
from icelib.tools.search.resultsdb.connect import connect

from app_builder import build_argparser as builder_build_argparser
from app_builder import build_binary, get_build_dir, setup_build
from app_runner import build_argparser as runner_build_argparser
from app_runner import prepare as prepare_run
from locus_lib import get_median_metric
from locus_lib import regenerate
from logger import QaasComponents, log
from oneview_runner import parse_lprof_loop_profile, LPROF_TIME_METRIC
from util import generate_timestamp_str

script_dir=os.path.dirname(os.path.realpath(__file__))
template_dir=os.path.join(script_dir, '..', 'templates')
tmp_dir="/nfs/site/proj/alac/tmp/qaas-locus-runs"


def instantiate_template(template_file, names, out_dir, outfile_name):
    scop_template = Template.compile(file=os.path.join(template_dir, template_file))
    scop_def = scop_template(searchList=[names])
    full_filename=os.path.join(out_dir, outfile_name)
    print(scop_def, file=open(full_filename, 'w'))
    return full_filename

#def generate_locus_file_and_scripts(dbfile, run_dir, compiler, src_file, codelet_name, locus_bin_run_dir, inc_flags):
#    iceorig_file, locus_outfile_suffix, build_cmd_sh_file, timing_script_file, timing_fn_name = generate_build_run_timing_scripts(run_dir, src_file, codelet_name, locus_bin_run_dir)
#
#    locus_file, preproc_folders, locus_run_cmd = generate_locus_command(dbfile, src_file, codelet_name, inc_flags, locus_outfile_suffix, timing_script_file, timing_fn_name)
#                    
#    # returning iceorig_file to be restored by build_cmd script after each Locus search step
#    # Also return locus_run_cmd to be used
#    return iceorig_file, locus_run_cmd, dbfile, locus_file, preproc_folders, build_cmd_sh_file

def generate_locus_command(dbfile, src_file, inc_flags, locus_outfile_suffix, timing_script_file, timing_fn_name):
    # Locus will invoke build_cmd script and that script will make use of full_iceorig_file to restore back to full_src_file
    #engine='exhaustive'
    engine='opentuner'
    ntests=500
    #ntests=50
    locus_file='scop.locus'
    preproc_folders = [part.strip() for part in inc_flags.split("-I") if part]
    preproc_folders_str = " ".join(preproc_folders)
    locus_run_cmd = [f'ice-locus-{engine}.py --database {dbfile} -f {src_file} '
                    f'-t {locus_file} -o suffix --search --ntests {ntests} --tfunc {timing_script_file}:{timing_fn_name} '
                    f'--preproc {preproc_folders_str} '
                    f'--suffixinfo qaas --equery --no-applyDFAOpt --suffix {locus_outfile_suffix} --debug' ]
                    
    return locus_file,preproc_folders,locus_run_cmd

def generate_build_script(run_dir, src_file, codelet_name, make_cmd, names):
    #src_file='bt.c_compute_rhs_line1892_loop.c'
    #src_file='bt.c_compute_rhs_line1907_loop.c'
    iceorig_file=src_file+'.iceorig'
    locus_outfile_suffix='.opt'
    opt_file=re.sub('\.c$',f'{locus_outfile_suffix}.c', src_file)
    exe_file=codelet_name
    build_cmd_sh_file='buildcmd.sh'

    names.update({
        "exe_file": exe_file, 
        "orig_build_type_name": "orig", "opt_build_type_name": "opt",
        "src_file": src_file, 
        "iceorig_file": iceorig_file, "opt_file": opt_file, 
        "build_cmd": f"{make_cmd}"
    })

    full_build_cmd_sh_file = instantiate_template(build_cmd_sh_file+'.template', names, run_dir, build_cmd_sh_file)
    os.chmod(full_build_cmd_sh_file, stat.S_IRWXU)
    return iceorig_file, locus_outfile_suffix, build_cmd_sh_file, names

def generate_run_script(run_dir, locus_bin_run_dir):
    run_cmd_sh_file='runcmd.sh'

    run_cmd=f'python {script_dir}/app_runner.py' \
		+ f" --binary-path $QAAS_binary_path" \
		+ f" --run-dir $QAAS_run_dir" \
		+ f" --data-path $QAAS_data_path" \
		+ f" --mode run" \
		+ f" --run-cmd \"$QAAS_run_cmd\""

    # Names for template instantiation
    names = {
        'locus_run_dir': run_dir,
        "run_cmd": f"{run_cmd}",
        "locus_bin_run_dir": locus_bin_run_dir
    }
    full_run_cmd_sh_file = instantiate_template(run_cmd_sh_file+'.template', names, run_dir, run_cmd_sh_file)
    os.chmod(full_run_cmd_sh_file, stat.S_IRWXU)
    return run_cmd_sh_file,names

def generate_build_cmd():
    make_cmd=f'python {script_dir}/app_builder.py' \
        + f" --src-dir $QAAS_locus_src_dir" \
		+ " --mode make " \
		+ f" --output-binary-path $QAAS_binary_path" \
		+ f" --compiler-dir $QAAS_compiler_dir" \
		+ f" --orig-user-CC $QAAS_orig_user_CC" \
		+ f" --target-CC $QAAS_user_CC" \
		+ f" --user-c-flags \"$QAAS_user_c_flags\"" \
		+ f" --user-cxx-flags \"$QAAS_user_cxx_flags\"" \
		+ f" --user-fc-flags \"$QAAS_user_fc_flags\"" \
		+ f" --user-link-flags \"$QAAS_user_link_flags\"" \
		+ f" --user-target $QAAS_user_target" \
		+ f" --user-target-location $QAAS_user_target_location"

    return make_cmd

def generate_locus_scripts(run_dir, names, build_cmd_sh_file, 
                           run_cmd_sh_file, insert_pragma_before_line,
                           locus_bin):
    timing_script_file='loreTiming.py'
    timing_fn_name='getTimingQaas' 
    # the pragma will shift the loop head down by 1
    new_loop_head_line_num = insert_pragma_before_line + 1
    names.update({
        "build_cmd_sh": build_cmd_sh_file, "run_cmd_sh": run_cmd_sh_file,
        "timing_script_file": timing_script_file, "timing_fn_name": timing_fn_name,
        "timing_script_loop_head": new_loop_head_line_num,
        "locus_bin": locus_bin
    })
    instantiate_template('scop.locus.template', names, run_dir,"scop.locus")
    instantiate_template(timing_script_file+'.template', names, run_dir, timing_script_file)
    return timing_script_file, timing_fn_name

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
def exec(src_dir, compiler_dir, output_binary_path, orig_user_CC, user_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
         binary_path, run_dir, data_path, run_cmd, env_var_map, target_location):
    my_env = os.environ.copy()

    locus_ts_str = generate_timestamp_str()
    run_dir = os.path.join(tmp_dir, f"run-{locus_ts_str}")

    os.makedirs(run_dir)

    locus_src_dir = os.path.join(run_dir, 'src')
    locus_bin_run_dir = os.path.join(run_dir, 'run')
    locus_bin = os.path.join(locus_bin_run_dir, 'pgm')
    locus_result_dir = os.path.join(run_dir, 'results')

    # copy source tree to run_dir for Locus processing
    shutil.copytree(src_dir, locus_src_dir, symlinks=True)

    
    build_dir, output_dir, output_name, env = setup_build(locus_src_dir, compiler_dir, locus_bin, orig_user_CC, user_CC, 
                                                          user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags)
    make_cmd = generate_build_cmd()

    run_cmd_sh_file, template_names = generate_run_script(run_dir, locus_bin_run_dir)

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
    subprocess.run(make_sh_cmd, shell=True, env=env, cwd=run_dir)
    build_dir = get_build_dir(locus_src_dir)
    compile_command_json_file = os.path.join(build_dir, 'compile_commands.json')


    

#1.5 setup trial run to select loops (before insert of Locus pragma)
    prepare_run(locus_bin, locus_bin_run_dir, data_path)

    run_sh_cmd=f'./{run_cmd_sh_file}'
    env["QAAS_run_dir"]=f"{locus_bin_run_dir}"
    env["QAAS_data_path"]=f"{data_path}"
    env["QAAS_run_cmd"]=f"{run_cmd}"
    # below command try the run script
    subprocess.run(run_sh_cmd, shell=True, env=env, cwd=run_dir)
    loop_profile_df = parse_lprof_loop_profile(env, locus_bin_run_dir, locus_bin)
    # Sort reversing of time
    loop_profile_df.sort_values(by = LPROF_TIME_METRIC, ascending=False)
    # Now pick the hottest loop for tuning
    # TODO: setup with budget in mind to try more loops and/or specific loops
    target_loop_profile_df = loop_profile_df.head(1)
    target_loop_path = target_loop_profile_df['Loop Path'].item()
    target_outter_loop_loc = target_loop_path[0]
    full_src_file, target_line_no = target_outter_loop_loc.split(':')
    insert_pragma_before_line = int(target_line_no)

    print(full_src_file)

    src_folder=os.path.dirname(full_src_file)

    full_iceorig_file, locus_outfile_suffix, build_cmd_sh_file, template_names = \
        generate_build_script(run_dir, full_src_file, 'conv', make_cmd, template_names)
    timing_script_file, timing_fn_name = generate_locus_scripts(run_dir, template_names, build_cmd_sh_file, run_cmd_sh_file, insert_pragma_before_line, locus_bin)

    # Setup dep file needed for Locus runs
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
    
# 1. save <file> to <file>.orig to restore at the end
    restore_src_file=full_src_file + '.orig'
    shutil.copy2(full_src_file, restore_src_file) # save restore file

# 2. Add, in place, file <file> ICE pragma  (<file> now updated to contain ICE pragma)
    with open(full_src_file, 'r') as rd:
        lines = rd.readlines()
    with open(full_src_file, 'w') as wr:
        for line_num, line in enumerate(lines):
            if line_num + 1 == insert_pragma_before_line:
                wr.write('#pragma @ICE loop=scop\n')
            wr.write(line)
    # input(f'check file: {full_src_file}')


# 3. Copy <file> to <file>.iceorig
    # full_src_file now have ICE pragma instead
    # save to iceorig file.  Note this file will be used by build_cmd scrpt to restore it after each Locus search step
    shutil.copy2(full_src_file, full_iceorig_file) 


    
    # Will be created by Locus
    dbfile=os.path.join(run_dir,'lore-locus.db')

    locus_file, header_folders, locus_run_cmd = generate_locus_command(dbfile, full_src_file, inc_flags, locus_outfile_suffix, timing_script_file, timing_fn_name)

    print(full_iceorig_file)
    print(locus_run_cmd)
    print(dbfile)

# 4. Invoke Locus with <file> as input and suffix .opt so output <file>.opt
# 5. In build command (NOT IN PYTHON SCRIPT), 
#   a. mv <file>.opt to <file>
#   b. proceed to normal building procedure (so LORE output file will be used)
#   c. cp <file>.iceorig to <file> to restore it for next steps of search
    
    print(locus_run_cmd)
#    with open('/tmp/env.txt', 'w') as f:
#        for line in [f'{k}={v}' for k,v in env.items()]:
#            f.write('export '+line+'\n')
    # Add script directory to ensure getTiming script can use QaaS scripts
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f'{env["PYTHONPATH"]}:{script_dir}'
    else:
        env['PYTHONPATH'] = script_dir
    subprocess.run(locus_run_cmd, shell=True, env=env, cwd=run_dir)

# 6. after all is done (reverse operation of #1)
#   mv <file>.orig <file>
    shutil.copy2(restore_src_file, full_src_file) 


    if extract_best_variant(dbfile, locus_file, locus_result_dir, header_folders):
        # Best variant regenerated in place, so rebuild will produce opt executable
        os.remove(locus_bin)
        build_binary(user_target, build_dir, target_location, env, output_dir, output_name)
        # Copy the binary to result directory 
        os.makedirs(os.path.dirname(output_binary_path), exist_ok=True)
        shutil.copy2(locus_bin, output_binary_path)


# Return True if best variant generated False if not
def extract_best_variant(db_path, lfname, result_dir, header_folders):
    debug = False
    engine, session = connect('sqlite:///'+db_path, debug)
    variants = (session.query(m.Variant)
                .join(m.Search, m.Search.id == m.Variant.searchid)
                .join(m.LocusFile)
                .filter(m.LocusFile.locusfilename == lfname))
    min_median = float("inf")
    min_median_variant = None
    for var in variants:
        unit, median_metric = get_median_metric(var)
        assert unit == LPROF_TIME_METRIC
        if median_metric < min_median:
            min_median_variant = var
            min_median = median_metric
    if min_median_variant:
        x = session.query(m.Search,m.LocusFile.locusfilename).join(m.LocusFile)
        # Found the best variant, regenerate source and locus file
        workdir=os.path.join(result_dir, f'v-{min_median_variant.id}')
        regenerate(session, x, workdir, int(min_median_variant.id), header_folders)
        # Note the source code is regenerated in place to replace the source file
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Run mutator in QaaS")
    # Builder flags
    builder_build_argparser(parser, include_mode=False)

    # runner flags
    runner_build_argparser(parser, include_mode=False)
    args = parser.parse_args()
    env_var_map = dict([(v.split("=",1)) for v in args.var]) 
    exec(args.src_dir, args.compiler_dir, args.output_binary_path, args.orig_user_CC, args.target_CC,
         args.user_c_flags, args.user_cxx_flags, args.user_fc_flags, args.user_link_flags, args.user_target,
         args.binary_path, args.run_dir, args.data_path, args.run_cmd, env_var_map, args.user_target_location)

if __name__ == "__main__": 
    main()
