# -*- coding: utf-8 -*-
"""
Configuration, including options fetched from ISDB API.
"""
import json
import os
from . import MODULE_DIR

AIF_REQUIRED = {} #loads AIF keynames with required tag from JSON file into dictionary
AIF_OPTIONAL = {}
LABEL_TO_NAME_REQ = {}
LABEL_TO_NAME_OPT = {}
AIF_VERSION = '9d1c623'

AIF_LOOPS = []
AIF_LOOP_NAMES = {}
with open('aifdictionary.json', 'r', encoding='utf-8') as json_dict:
    json_dict = json.load(json_dict)


for item in json_dict:
    if item['required'] == 'True':
        if item['data name'] == '_audit_aif_version':
            pass
        else:
            AIF_REQUIRED[item['label']] = item['description']
            LABEL_TO_NAME_REQ[item['label']] =item['data name']

#print(json_dict)

substring1 = '_adsorp_'
substring2 = '_desorp_'

for item in json_dict:
    if substring1 in item['data name']:
        AIF_LOOPS += [item['label']]
        AIF_LOOP_NAMES[item['label']] = item['data name']
        #print('success')
    elif substring2 in item['data name']:
        AIF_LOOPS += [item['label']]
        AIF_LOOP_NAMES[item['label']] = item['data name']
        #print('success2')
    elif item['required'] == 'False':
        AIF_OPTIONAL[item['label']] = item['description']
        LABEL_TO_NAME_OPT[item['label']] = item['data name']

SINGLE_COMPONENT_EXAMPLE = \
"""#pressure,adsorption
0.310676,0.019531
5.13617,0.000625751
7.93711,0.0204602
12.4495,0.06066
30.0339,0.159605
44.8187,0.200392
58.3573,0.270268
66.2941,0.300474
72.9855,0.340276"""

SUBMISSION_FOLDER = os.getenv('DIGITIZER_SUBMISSION_FOLDER', os.path.join(MODULE_DIR, os.pardir, 'submissions'))
STATIC_DIR = os.path.join(MODULE_DIR, 'static')
TEMPLATES_DIR = os.path.join(MODULE_DIR, 'templates')

DEFAULT_ISOTHERM_FILE = os.path.join(STATIC_DIR, 'default_isotherm.json')
