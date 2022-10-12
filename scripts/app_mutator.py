# Contributors: Padua/Yoonseo
import os
import re
import subprocess
import stat
import shutil
from logger import log, QaasComponents
from Cheetah.Template import Template

script_dir=os.path.dirname(os.path.realpath(__file__))
template_dir=os.path.join(script_dir, 'templates')

def instantiate_template(template_file, names, out_dir, outfile_name):
    scop_template = Template.compile(file=os.path.join(template_dir, template_file))
    scop_def = scop_template(searchList=[names])
    full_filename=os.path.join(out_dir, outfile_name)
    print(scop_def, file=open(full_filename, 'w'))
    return full_filename

def generate_locus_file_and_scripts(dbfile, run_dir, compiler, src_file, num_cores, old_layout):
    #src_file='bt.c_compute_rhs_line1892_loop.c'
    #src_file='bt.c_compute_rhs_line1907_loop.c'
    iceorig_file=src_file+'.iceorig'
    locus_outfile_suffix='.opt'
    opt_file=re.sub('\.c$',f'{locus_outfile_suffix}.c', src_file)
    codelet_name=re.sub('_loop\.c$','', src_file) if old_layout else re.sub('_loop\.c\.0\.c$','', src_file)
    exe_file=codelet_name
    build_cmd_sh_file='buildcmd.sh'
    run_cmd_sh_file='runcmd.sh'
    timing_script_file='loreTiming.py'
    timing_fn_name='getTiming' if old_layout else 'getTimingNew'

    # Names for template instantiation
    names = {
        "src_file": src_file, "iceorig_file": iceorig_file, "opt_file": opt_file, "exe_file": exe_file, 
        "build_cmd_sh": build_cmd_sh_file, "run_cmd_sh": run_cmd_sh_file,
        "build_cmd": f"make CC={compiler} CCFAMILY={compiler} ./{exe_file}",
        "run_cmd": f"taskset -c {num_cores-1} ./{exe_file} ../input 100",
        "orig_build_type_name": "orig", "opt_build_type_name": "opt",
        "timing_script_file": timing_script_file, "timing_fn_name": timing_fn_name
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
    locus_run_cmd = [f'ice-locus-{engine}.py --database {dbfile} -f {src_file} '
                    f'-t scop.locus -o suffix --search --ntests {ntests} --tfunc {timing_script_file}:{timing_fn_name} '
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
    subprocess.run(locus_run_cmd, shell=True, cwd=run_dir, env=my_env)
    shutil.copy2(os.path.join(run_dir, restore_src_file), full_src_file) 

def exec(src_dir, compiler_dir, relative_binary_path, locus_run_dir):
    log(QaasComponents.APP_MUTATOR, f'Tuning source code from {src_dir} to be compiled by {compiler_dir}', mockup=True)
    opt_binary = os.path.join(src_dir, relative_binary_path)
    # Will be created by Locus
    dbfile=os.path.join(locus_run_dir,'lore-locus.db')
    log(QaasComponents.APP_MUTATOR, f'Locus DB: {dbfile}')
    return opt_binary
    run_mutator(dbfile, compiler, full_src_file, num_cores)
    log(QaasComponents.APP_MUTATOR, f'Output to Optimized binary {opt_binary}', mockup=True)
    return opt_binary