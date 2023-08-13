# ! pip install icd10-cm


# import pandas as pd
# from google.colab import drive
# drive.mount('/content/drive')

import csv
import re
import pickle
import os
from functools import reduce
from collections import defaultdict
import icd10

def extract_codes_from_text(text):
    text = text[2:-2]
    code_sublists = []
    for sublist_text in text.split('", "'):
        sublist_text = sublist_text[1:-1]
        codes = [code.strip()[1:-1] for code in sublist_text.split(',')]
        code_sublists.append(codes)
    return code_sublists

def load_data_and_extract_codes(input_file):
    with open(input_file, 'r') as csvfile:
        rows = list(csv.reader(csvfile, delimiter=','))
    codes_list = []
    for row in rows[1:]:
        code_sublists = extract_codes_from_text(row[6])
        codes_list.append(code_sublists)
    return codes_list

def find_ancestors_for_icd_code(icd_code, icd_code_to_ancestors):
    if icd_code in icd_code_to_ancestors:
        return
    icd_code_to_ancestors[icd_code] = []
    ancestor = icd_code[:]
    while len(ancestor) > 2:
        ancestor = ancestor[:-1]
        if ancestor[-1] == '.':
            ancestor = ancestor[:-1]
        if icd10.find(ancestor) is not None:
            icd_code_to_ancestors[icd_code].append(ancestor)

def build_icd_code_to_ancestors_dict(input_file, pkl_file):
    if os.path.exists(pkl_file):
        icd_code_to_ancestors = pickle.load(open(pkl_file, 'rb'))
        return icd_code_to_ancestors

    codes_list = load_data_and_extract_codes(input_file)
    all_codes = set(reduce(lambda x, y: x + y, reduce(lambda x, y: x + y, codes_list)))
    icd_code_to_ancestors = defaultdict(list)
    for code in all_codes:
        find_ancestors_for_icd_code(code, icd_code_to_ancestors)
    pickle.dump(icd_code_to_ancestors, open(pkl_file, 'wb'))
    return icd_code_to_ancestors

# Usage: 
input_file = '/content/drive/MyDrive/Mtech /Dissertation/data_output/raw_data.csv'
pkl_file = "/model/icd_code_to_ancestors_dict.pkl"
icd_code_to_ancestors = build_icd_code_to_ancestors_dict(input_file, pkl_file)
all_codes_and_ancestors = set(icd_code_to_ancestors.keys())
print(all_codes_and_ancestors)
