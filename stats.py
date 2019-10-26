import datetime
import time
import os
import json
import datetime

from tools.degage import Dégage

# read configs
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    configs = json.loads(f.read())

degage = Dégage(config=configs[0])
# print driving stats
degage.percentage_of_kms()