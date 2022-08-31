from logger import log, QaasComponents

def show_results(db_address, timestamp):
    log(QaasComponents.RESULT_PRESENTER, f'Getting results from {db_address} with timestamp of {timestamp}', mockup=True)