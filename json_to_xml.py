import json
import pandas as pd
from pprint import pprint
import time

with open('results.json', 'r', encoding='utf-8') as jobs:
    entries = json.load(jobs)

# renamed = []
#
# for entry in entries:
#     keys = list(entry.keys())
#     renamed.append(dict())
#     for i in range(len(keys)):
#         new_key = '_'.join(keys[i].split(' '))
#         renamed[-1][new_key] = entry[keys[i]]
#     pprint(renamed[-1])

pprint(pd.DataFrame(entries).to_xml('results.xml', index=False))