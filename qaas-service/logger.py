from enum import Enum, auto

class Color(Enum):
    RED = '\033[31m'
    RESET = '\033[39;49m'
    BLACK = '\033[30m'
    GREEN = '\033[32m'
    ORANGE = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    LIGHTGREY = '\033[37m'
    DARKGREY = '\033[90m'
    LIGHTRED = '\033[91m'
    LIGHTGREEN = '\033[92m'
    YELLOW = '\033[93m'
    LIGHTBLUE = '\033[94m'
    PINK = '\033[95m'
    LIGHTCYAN = '\033[96m'
    WHITE = '\033[37m'

class QaasComponents(Enum):
    APP_BUILDER = Color.GREEN
    APP_MUTATOR = Color.ORANGE
    APP_RUNNER = Color.BLUE
    DB_POPULATOR = Color.PURPLE
    ENV_PROVISIONER = Color.CYAN
    OV_RUNNER = Color.YELLOW
    RESULT_PRESENTER = Color.PINK
    BUSINESS_LOGICS = Color.RED





def log(component, msg, mockup=False):
    prefix = f'{Color.WHITE.value}[MOCKUP]:{Color.RESET.value}' if mockup else ''
    component_color = component.value
    print(f'{prefix} {component_color.value}{msg}{Color.RESET.value}')