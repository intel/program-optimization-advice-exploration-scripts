#!/usr/bin/env python3
import os
import datetime
import qaas


# Demo with preset values
QAAS_COMPILERS_DIRECTORY='/nfs/site/proj/openmp/compilers'
QAAS_ONEVIEW_DIRECTORY='/nfs/site/proj/openmp/compilers'

QAAS_ROOT='/tmp/qaas'

QAAS_DB_ADDRESS='MOCKUP DB ADDRESS'

if not os.path.isdir(QAAS_ROOT):
    os.makedirs(QAAS_ROOT)

qaas.run(QAAS_ROOT, QAAS_DB_ADDRESS)