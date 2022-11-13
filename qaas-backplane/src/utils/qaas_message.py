import pickle

class QaasMessage:
    def __init__(self, info):
        self.info = info

    def is_end_job(self):
        return False

    def encode(self):
        return pickle.dump(self)

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