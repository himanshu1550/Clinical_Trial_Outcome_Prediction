# import pandas as pd
# from google.colab import drive
# drive.mount('/content/drive')

import csv
import os
from tqdm import tqdm
from xml.etree import ElementTree as ET

def extract_dates(root, tag):
    date_element = root.find(tag)
    if date_element is not None:
        return date_element.text
    return ''

def xmlfile_2_date(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    start_date = extract_dates(root, 'start_date')
    completion_date = extract_dates(root, 'primary_completion_date') or extract_dates(root, 'completion_date')
    return start_date, completion_date

raw_folder = "/content/raw_data"

def process_data(input_file, output_file):
    with open(input_file) as fin, open(output_file, 'w') as fout:
        readers = list(csv.reader(fin))[1:]
        total_num, start_num, completion_num = 0, 0, 0
        for row in tqdm(readers):
            nctid = row[0]
            file = os.path.join(raw_folder, f"{nctid[:7]}xxxx/{nctid}.xml")
            start_date, completion_date = xmlfile_2_date(file)
            if start_date:
                start_num += 1
            if completion_date:
                completion_num += 1
            total_num += 1
            fout.write(f"{nctid}\t{start_date}\t{completion_date}\n")
        print("total_num", total_num)
        print("start_num", start_num)
        print("completion_num", completion_num)

process_data("/content/drive/MyDrive/Mtech /Dissertation/data_output/raw_data.csv", "/raw_data_folder/nctid_date.txt")
