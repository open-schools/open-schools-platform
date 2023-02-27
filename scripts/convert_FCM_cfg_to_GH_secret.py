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

f = open("firebase_admin_config").readlines()
print(convert_config_to_secret(f))
