import os
import sys
from pathlib import Path


def convert_config_to_secret(config):
    s = ""
    for i in config:
        s += i.replace("\n", "").replace("\"", "\\\"").replace("{", "\\{").replace("}", "\\}"). \
            replace("\\n", "\\\\n")

    return s


BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()

frame = sys._getframe()

FIREBASE_ADMIN_CONFIG = os.path.join(BASE_DIR, '.firebase_admin_config')

print(convert_config_to_secret(open(FIREBASE_ADMIN_CONFIG).readlines()))
