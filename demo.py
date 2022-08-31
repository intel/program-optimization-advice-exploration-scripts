#!/usr/bin/env python3
# Contributors: Hafid/David
import os
import datetime
import qaas


# Demo with preset values
QAAS_COMPILERS_DIRECTORY='/nfs/site/proj/openmp/compilers'
QAAS_ONEVIEW_DIRECTORY='/nfs/site/proj/alac/software/UvsqTools/20211001'

QAAS_ROOT='/tmp/qaas'

QAAS_DB_ADDRESS='MOCKUP DB ADDRESS'

if not os.path.isdir(QAAS_ROOT):
    os.makedirs(QAAS_ROOT)

qaas.run(QAAS_ROOT, QAAS_DB_ADDRESS, QAAS_COMPILERS_DIRECTORY, QAAS_ONEVIEW_DIRECTORY)