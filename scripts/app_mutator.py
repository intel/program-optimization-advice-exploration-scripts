# Contributors: Padua/Yoonseo
import json
import datetime
import argparse
import os
import re
import subprocess
import stat
import shutil
from logger import log, QaasComponents
from Cheetah.Template import Template
from app_builder import build_argparser as builder_build_argparser
from app_runner import build_argparser as runner_build_argparser
from app_builder import setup_build, build_binary, get_build_dir
from app_runner import prepare as prepare_run

script_dir=os.path.dirname(os.path.realpath(__file__))
template_dir=os.path.join(script_dir, '..', 'templates')
tmp_dir="/nfs/site/proj/alac/tmp/qaas-locus-runs"

def instantiate_template(template_file, names, out_dir, outfile_name):
    scop_template = Template.compile(file=os.path.join(template_dir, template_file))
    scop_def = scop_template(searchList=[names])
    full_filename=os.path.join(out_dir, outfile_name)
    print(scop_def, file=open(full_filename, 'w'))
    return full_filename

def generate_locus_file_and_scripts(dbfile, run_dir, compiler, src_file, codelet_name, locus_bin_run_dir, inc_flags):
    #src_file='bt.c_compute_rhs_line1892_loop.c'
    #src_file='bt.c_compute_rhs_line1907_loop.c'
    iceorig_file=src_file+'.iceorig'
    locus_outfile_suffix='.opt'
    opt_file=re.sub('\.c$',f'{locus_outfile_suffix}.c', src_file)
    exe_file=codelet_name
    build_cmd_sh_file='buildcmd.sh'
    run_cmd_sh_file='runcmd.sh'
    timing_script_file='loreTiming.py'
    timing_fn_name='getTimingNew' 

    make_cmd=f'python {script_dir}/app_builder.py' \
        + f" --src-dir $QAAS_locus_src_dir" \
		+ " --mode make " \
		+ f" --relative-binary-path $QAAS_binary_path" \
		+ f" --compiler-dir $QAAS_compiler_dir" \
		+ f" --orig-user-CC $QAAS_orig_user_CC" \
		+ f" --target-CC $QAAS_user_CC" \
		+ f" --user-c-flags \"$QAAS_user_c_flags\"" \
		+ f" --user-cxx-flags \"$QAAS_user_cxx_flags\"" \
		+ f" --user-fc-flags \"$QAAS_user_fc_flags\"" \
		+ f" --user-link-flags \"$QAAS_user_link_flags\"" \
		+ f" --user-target $QAAS_user_target"
    run_cmd=f'python {script_dir}/app_runner.py' \
		+ f" --binary-path $QAAS_binary_path" \
		+ f" --run-dir $QAAS_run_dir" \
		+ f" --data-path $QAAS_data_path" \
		+ f" --mode run" \
		+ f" --run-cmd \"$QAAS_run_cmd\""

    # Names for template instantiation
    names = {
        "src_file": src_file, "iceorig_file": iceorig_file, "opt_file": opt_file, "exe_file": exe_file, 
        "build_cmd_sh": build_cmd_sh_file, "run_cmd_sh": run_cmd_sh_file,
        "build_cmd": f"{make_cmd}",
        "run_cmd": f"{run_cmd}",
        "orig_build_type_name": "orig", "opt_build_type_name": "opt",
        "timing_script_file": timing_script_file, "timing_fn_name": timing_fn_name, 'locus_run_dir': run_dir,
        "locus_bin_run_dir": locus_bin_run_dir
    }

    instantiate_template('scop.locus.template', names, run_dir,"scop.locus")
    full_build_cmd_sh_file = instantiate_template(build_cmd_sh_file+'.template', names, run_dir, build_cmd_sh_file)
    full_run_cmd_sh_file = instantiate_template(run_cmd_sh_file+'.template', names, run_dir, run_cmd_sh_file)
    os.chmod(full_build_cmd_sh_file, stat.S_IRWXU)
    os.chmod(full_run_cmd_sh_file, stat.S_IRWXU)
    instantiate_template(timing_script_file+'.template', names, run_dir, timing_script_file)

    # Locus will invoke build_cmd script and that script will make use of full_iceorig_file to restore back to full_src_file
    #engine='exhaustive'
    engine='opentuner'
    ntests=500
    #ntests=50
    preproc_folders=" ".join([part.strip() for part in inc_flags.split("-I") if part])
    locus_run_cmd = [f'ice-locus-{engine}.py --database {dbfile} -f {src_file} '
                    f'-t scop.locus -o suffix --search --ntests {ntests} --tfunc {timing_script_file}:{timing_fn_name} '
                    f'--preproc {preproc_folders} '
                    f'--suffixinfo {codelet_name}  --equery --no-applyDFAOpt --suffix {locus_outfile_suffix} --debug' ]
                    
    # returning iceorig_file to be restored by build_cmd script after each Locus search step
    # Also return locus_run_cmd to be used
    return iceorig_file, locus_run_cmd, dbfile 

# Execution scheme:
# 
# Given original file <file>
# save <file> to <file>.orig to restore at the end
#
# Change, in place, file <file> original pragma to ICE pragma  (<file> now updated to contain ICE pragma)
# Copy <file> to <file>.iceorig
# Invoke LORE with <file> as input and suffix .opt so output <file>.opt
# In build command (NOT IN PYTHON SCRIPT), 
#   mv <file>.opt to <file>
#   proceed to normal building procedure (so LORE output file will be used)
#   cp <file>.iceorig to <file> to restore it for next steps of search
# after all is done
#   mv <file>.orig <file>
def run_mutator(dbfile, compiler, full_src_file, num_cores):
    run_dir = os.path.dirname(full_src_file)
    src_file = os.path.basename(full_src_file)

    #num_cores = multiprocessing.cpu_count()
    old_layout = os.path.split(run_dir)[1] == 'extractedLoops'

    iceorig_file, locus_run_cmd, dbfile = generate_locus_file_and_scripts(dbfile, run_dir, 
        compiler, src_file, num_cores, old_layout)

    #full_src_file=os.path.join(run_dir, src_file0)
    restore_src_file=src_file + '.orig'
    full_iceorig_file=os.path.join(run_dir, iceorig_file)


    shutil.copy2(full_src_file, os.path.join(run_dir, restore_src_file)) # save restore file
    input('test')
    with open(full_src_file, 'r') as rd:
        lines = rd.readlines()
    # change #pragma scop to ICE pragma
    visited_begin_pragma_scop = False
    with open(full_src_file, 'w') as wr:
        for line in lines:
            if re.match('#pragma scop', line):
                if old_layout:
                    # old layout format:
                    # #pragma scop
                    #    for...
                    # so replace pragma in place
                    line = re.sub('#pragma scop', '#pragma @ICE loop=scop', line)
                else:
                    # new layout format:
                    # #pragma scop
                    # {
                    #    for...
                    # }
                    # so insert pragma after bracket
                    line = re.sub('#pragma scop', '', line)
                    visited_begin_pragma_scop = True
            if re.match('{', line) and old_layout is False and visited_begin_pragma_scop is True:
                # write the original bracket line
                wr.write(line)
                # insert the ICE pragma after this bracket
                line = '#pragma @ICE loop=scop\n'
                visited_begin_pragma_scop = False
            line = re.sub('#pragma endscop', '', line)
            wr.write(line)
    # full_src_file now have ICE pragma instead
    # save to iceorig file.  Note this file will be used by build_cmd scrpt to restore it after each Locus search step
    shutil.copy2(full_src_file, full_iceorig_file) 

    my_env=os.environ.copy()
    my_env['LORE_CC_VERSION'] = subprocess.run([compiler, '--version'], capture_output=True, text=True).stdout.split('\n')[0]
    my_env['LORE_CC'] = compiler
    my_env['LORE_CXX'] = compiler
    #subprocess.run(locus_run_cmd, shell=True, cwd=run_dir, env=my_env)
    shutil.copy2(os.path.join(run_dir, restore_src_file), full_src_file) 

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
def exec(src_dir, compiler_dir, relative_binary_path, orig_user_CC, user_CC, 
         user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags, user_target,
         binary_path, run_dir, data_path, run_cmd, env_var_map):
    my_env = os.environ.copy()

    locus_timestamp = int(round(datetime.datetime.now().timestamp()))
    locus_ts_str = str(locus_timestamp)
    locus_ts_str = locus_ts_str[:3] + "-" + locus_ts_str[4:6] + "-" + locus_ts_str[7:]
    run_dir = os.path.join(tmp_dir, f"run-{locus_ts_str}")

    os.makedirs(run_dir)

    locus_src_dir = os.path.join(run_dir, 'src')
    locus_bin_run_dir = os.path.join(run_dir, 'run')
    locus_bin = os.path.join(locus_bin_run_dir, 'pgm')
    # TODO: fix hardcoding
    #full_src_file = os.path.join(locus_src_dir, 'nn-codelets/conv_op/direct_conv/1.1/1.1_back_prop_sx5/codelet.c')
    full_src_file = os.path.join(locus_src_dir, 'nn-codelets/conv_op/direct_conv/1.2/1.2_back_prop_sx5/codelet.c')
    print(full_src_file)
    src_folder=os.path.dirname(full_src_file)

    # copy source tree to run_dir for Locus processing
    shutil.copytree(src_dir, locus_src_dir, symlinks=True)

    
    build_dir, output_dir, output_name, env = setup_build(locus_src_dir, compiler_dir, locus_bin, orig_user_CC, user_CC, 
                                                          user_c_flags, user_cxx_flags, user_fc_flags, user_link_flags)
    #build_binary(user_target, build_dir, env, output_dir, output_name)
    # See script generation function for the user of these variables
    make_sh_cmd="./buildcmd.sh"
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

    # below command try the make script
    subprocess.run(make_sh_cmd, shell=True, env=env, cwd=run_dir)
    build_dir = get_build_dir(locus_src_dir)
    compile_command_json_file = os.path.join(build_dir, 'compile_commands.json')
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


    # Will be created by Locus
    dbfile=os.path.join(run_dir,'lore-locus.db')

    full_iceorig_file, locus_run_cmd, dbfile = generate_locus_file_and_scripts(dbfile, run_dir, 
        user_CC, full_src_file, 'conv', locus_bin_run_dir, inc_flags)
    print(full_iceorig_file)
    print(locus_run_cmd)
    print(dbfile)
    
# 1. save <file> to <file>.orig to restore at the end
    restore_src_file=full_src_file + '.orig'
    shutil.copy2(full_src_file, restore_src_file) # save restore file


# 2. Add, in place, file <file> ICE pragma  (<file> now updated to contain ICE pragma)
#   TODO: Fix hardcoding
    #insert_pragma_before_line = 72
    insert_pragma_before_line = 74
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



    prepare_run(locus_bin, locus_bin_run_dir, data_path)

    run_sh_cmd="./runcmd.sh"
    env["QAAS_run_dir"]=f"{locus_bin_run_dir}"
    env["QAAS_data_path"]=f"{data_path}"
    env["QAAS_run_cmd"]=f"{run_cmd}"
    # below command try the run script
    #subprocess.run(run_sh_cmd, shell=True, env=env, cwd=run_dir)

    print(locus_run_cmd)
    with open('/tmp/env.txt', 'w') as f:
        for line in [f'{k}={v}' for k,v in env.items()]:
            f.write('export '+line+'\n')
    subprocess.run(locus_run_cmd, shell=True, env=env, cwd=run_dir)

# 6. after all is done (reverse operation of #1)
#   mv <file>.orig <file>
    shutil.copy2(restore_src_file, full_src_file) 


# def exec(src_dir, compiler_dir, relative_binary_path, locus_run_dir):
#     log(QaasComponents.APP_MUTATOR, f'Tuning source code from {src_dir} to be compiled by {compiler_dir}', mockup=True)
#     opt_binary = os.path.join(src_dir, relative_binary_path)
#     # Will be created by Locus
#     dbfile=os.path.join(locus_run_dir,'lore-locus.db')
#     log(QaasComponents.APP_MUTATOR, f'Locus DB: {dbfile}')
#     return opt_binary
#     run_mutator(dbfile, compiler, full_src_file, num_cores)
#     log(QaasComponents.APP_MUTATOR, f'Output to Optimized binary {opt_binary}', mockup=True)
#     return opt_binary

def main():
    parser = argparse.ArgumentParser(description="Run mutator in QaaS")
    # Builder flags
    builder_build_argparser(parser, include_mode=False)

    # runner flags
    runner_build_argparser(parser, include_mode=False)
    args = parser.parse_args()
    env_var_map = dict([(v.split("=",1)) for v in args.var]) 
    exec(args.src_dir, args.compiler_dir, args.relative_binary_path, args.orig_user_CC, args.target_CC,
         args.user_c_flags, args.user_cxx_flags, args.user_fc_flags, args.user_link_flags, args.user_target,
         args.binary_path, args.run_dir, args.data_path, args.run_cmd, env_var_map)

if __name__ == "__main__": 
    main()