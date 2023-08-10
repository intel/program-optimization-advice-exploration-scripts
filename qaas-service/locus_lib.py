import statistics as stat
import argparse
import os
import shutil
from icelib.frontend.optlang.optlanginterface import \
    argparser as optlangargparser
from icelib.util.constants import (ICE_OUTPUT_MODE_INPLACE,
                                   ICE_OUTPUT_MODE_STDOUT,
                                   ICE_OUTPUT_MODE_SUFFIX)
from icelib.frontend.optlang.locus.locusparser import LocusParser
import icelib.tools.search.searchbase as searchbase
from icelib.ice import ICE
from icelib.frontend.optlang.locus.optimizer import replEnvVars
from icelib.backend.genlocus import GenLocus
import icelib.tools.search.resultsdb.models as m
# Library to use Locus 

# Got this from dbutils.py of chartscripts
def saveenvvars(se, lfname):
    retinfo = {'lfname': lfname, 'searchtool': se.searchtool}
    envvars = {}
    for evalue in se.envvalues:
        varname = evalue.envvar.name
        if varname not in envvars:
            envvars[varname] = evalue.value 
        else:
            raise RuntimeError(f"Error getting env vars! Multiple values for {varname}!")
        #
    #
    retinfo['envdict'] = envvars
    return retinfo

# Get median metric and the unique unit of a variant
def get_median_metric(variant):
    expvalues = [e.expvalues for e in variant.experiments]
    units = [m.unit for l in expvalues for m in l]
            # Make sure unit is the same
    assert len(set(units)) == 1
    unit = units[0]
    emetrics = [m.metric for l in expvalues for m in l]
    medmetric = stat.median(emetrics)
    return unit,medmetric

from icelib.ice import argparser as iceargparser
def regenerate_source_file(all_srcfilenames, locus_out_file, dry_run, header_folders=None):
    argparser = argparse.ArgumentParser(add_help=True, 
                formatter_class=argparse.ArgumentDefaultsHelpFormatter, 
                parents=[iceargparser, optlangargparser])
            #srcfile='/host/nfs/site/proj/alac/data/UIUC-LORE/codelets/tmp/lore-codelets/full_src/all/NPB_2.3-OpenACC-C/BT/bt.c_compute_rhs_line1907_0/bt.c_compute_rhs_line1907_loop.c.0.c.iceorig.c'
            # TODO: Check with Thiago: may want to add an option to have no output at all
    output_mode = ICE_OUTPUT_MODE_STDOUT if dry_run else ICE_OUTPUT_MODE_INPLACE
    lp_args = ['--output', output_mode, '--srcfiles', *all_srcfilenames, '--optfile', locus_out_file]
    if header_folders: lp_args.extend(['--preproc', *header_folders])
    args = argparser.parse_args(lp_args) 
    from icelib.ice import init_logging as iceinit_logging
    args.rundirpath = iceinit_logging()
            # Have to save the locustree and use the saved optfile as ICE.run() tries to copy optfile
    lp = LocusParser(args.optfile, args.debug)
    ice_inst = ICE(lp, None, args)
    ice_inst.run()
    print(f'Regenerated source files:{all_srcfilenames}')
    return ice_inst

def regenerate_locus_file(session, envdict, v, workdir):
    conf_results=session.query(m.LocusFile).join(m.Configuration).filter(m.Configuration.id == v.configurationid)
    assert conf_results.count() == 1
            # Getting the only locus file
    lprog = conf_results.first()
    lparser = LocusParser()
    locustree = lparser.parse(lprog.data, False)
    searchnodes = {}
    replEnvVars(locustree, envdict)
    fakeparser = argparse.ArgumentParser()
    fakeparser.add_argument('--debug', required=False, action='store_true', default=False)
    fakeargs = fakeparser.parse_args([])
    searchbase.applyDFAOpts(locustree, fakeargs)
    searchbase.buildSearchNodes(locustree.topblk, searchnodes)
    for name, ent in locustree.items():
        searchbase.buildSearchNodes(ent, searchnodes)
    revertse = {}
    searchbase.convertDesiredResult(searchnodes, v.configuration.data, revertse)
            #locus_out_file='/tmp/out.scop.locus'
    locus_out_file=os.path.join(workdir, lprog.locusfilename)
    GenLocus.searchmode(locustree, locus_out_file)
    return locus_out_file
def regenerate(session, x, topdir, variant_id, header_folders=None):
    for se, lfname in x:
        envdict = saveenvvars(se, lfname)['envdict']
        searchdir=os.path.join(topdir, f'se-{se.id}')
        os.makedirs(searchdir)
        for sf in se.srcfiles:
            print(sf.data, file=open(os.path.join(searchdir, sf.srcfilename), 'w'))
        all_orig_srcfilenames=[os.path.join(searchdir, sf.srcfilename) for sf in se.srcfiles]
        for v in se.variants:
            if v.id == variant_id: 
                workdir=os.path.join(searchdir, f'v-{v.id}')
                os.makedirs(workdir)
                # Copy in original source code to be regenerated as transformed code (done by Locus inplace generation)
                for osf in all_orig_srcfilenames:
                    shutil.copy2(osf, workdir)
                all_srcfilenames=[os.path.join(workdir,sf.srcfilename) for sf in se.srcfiles]

                locus_out_file = regenerate_locus_file(session, envdict, v, workdir)
                ice_inst = regenerate_source_file(all_srcfilenames, locus_out_file, False, header_folders)
                print(f'Output source files at {workdir}')
    print('Finished file generation.')