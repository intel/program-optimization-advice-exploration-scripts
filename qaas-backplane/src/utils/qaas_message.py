import pickle
import socket

class QaasMessage:
    def __init__(self, info):
        self.info = info
        self.hostname = socket.gethostname()

    def is_end_job(self):
        return False

    def is_end_qaas(self):
        return False

    def encode(self):
        return pickle.dumps(self)

    def str(self):
        return self.info


class GeneralStatus(QaasMessage):
    def __init__(self, info):
        super().__init__(info)
    
class BeginJob(QaasMessage):
    def __init__(self):
        super().__init__("Job Begin")

class EndJob(QaasMessage):
    def __init__(self):
        super().__init__("Job End")

    def is_end_job(self):
        return True

class BeginQaas(QaasMessage):
    def __init__(self):
        super().__init__("QAAS Begin")

class EndQaas(QaasMessage):
    def __init__(self, output_ov_dir):
        super().__init__("QAAS End")
        self.output_ov_dir = output_ov_dir

    def is_end_qaas(self):
        return True