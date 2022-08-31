# Contributors: Yue/Cedric/Mathieu
from logger import log, QaasComponents

def populate(ov_run_dir, db_address, timestamp):
    log(QaasComponents.DB_POPULATOR, f"Pushing data of {ov_run_dir} to database at {db_address} with timestamp {timestamp}", mockup=True)