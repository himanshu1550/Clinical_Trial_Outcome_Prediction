import os, csv, pickle
from xml.dom import minidom
from xml.etree import ElementTree as ET
from collections import defaultdict
from time import time
import re
from tqdm import tqdm
import requests
from utils import root2outcome, get_icd_from_nih
from read_save_all_data import get_files_list


def xml_file_2_tuple(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    nctid = root.find('id_info').find('nct_id').text	### nctid: 'NCT00000102'
    study_type = root.find('study_type').text
    if study_type != 'Interventional':
      return (None,)  ### invalid

    interventions = [i for i in root.findall('intervention')]
    drug_interventions = [i.find('intervention_name').text for i in interventions \
                              if i.find('intervention_type').text=='Drug']
                              # or i.find('intervention_type').text=='Biological']
    if len(drug_interventions)==0:
      return (None,)

    try:
      status = root.find('overall_status').text
    except:
      status = ''
    # if status in drop_set:
    # 	return (None,)  ### invalid
    try:
      why_stop = root.find('why_stopped').text
    except:
      why_stop = ''
    label = root2outcome(root)
    label = -1 if label is None else label


    conditions = [i.text for i in root.findall('condition')]
    conditions = [i.lower() for i in conditions]
    return conditions, label, why_stop, None




def process_all(files):
    output_file = '/content/output/diseases.csv'
    t1 = time()
    disease_hit, disease_all = 0,0 ### disease hit icd && drug hit smiles
    input_file_lst = files
    disease2icd_and_cnt = dict()
    unfounded_disease_cnt = defaultdict(int)
    word_cnt = defaultdict(int)
    fieldname = ['disease', 'icd', 'count']

    data_count = 0
    for name in tqdm(input_file_lst[:]):
        result = xml_file_2_tuple(name)
        ## 0.1 & 0.2
        if len(result)==1:
            continue 	### only interventions
        conditions, label, why_stop, _ = result
        ## 0.4
        if (label == -1) and ('lack of efficacy' in why_stop or 'efficacy concern' in why_stop or \
        'accrual' in why_stop):
            label = 0
        ## 0.5
        if label == -1:
            continue
        data_count += 1
        icdcode_lst = []
        for disease in conditions:
            disease_all += 1
            disease_hit += 1
            if disease in disease2icd_and_cnt:
                disease2icd_and_cnt[disease][1] += 1
                if disease2icd_and_cnt[disease][0] == 'None':
                    disease_hit -= 1
                    unfounded_disease_cnt[disease] += 1
            else:
                codes = get_icd_from_nih(disease)
                if codes is None:
                    disease2icd_and_cnt[disease] = ['None', 1]
                    disease_hit -= 1
                    unfounded_disease_cnt[disease] += 1
                else:
                    disease2icd_and_cnt[disease] = [codes, 1]

    t2 = time()
    disease2cnt = sorted([(k,v) for k,v in unfounded_disease_cnt.items()], key = lambda x:x[1], reverse = True)
    for disease, cnt in disease2cnt:
        for word in disease.split():
            word_cnt[word] += cnt

    disease_icd_cnt = sorted([[disease,icd,cnt] for disease,(icd,cnt) in disease2icd_and_cnt.items()], key = lambda x:x[2], reverse=True)

    ### output
    with open(output_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldname)
        writer.writeheader()
        for disease, icd, cnt in disease_icd_cnt:
            writer.writerow({'disease':disease, 'icd':icd, 'count':cnt})


    ### use for debug
    with open('unfounded_disease_cnt.txt', 'w') as fout:
        for disease, cnt in disease2cnt:
            fout.write(disease + '\t\t' + str(cnt) + '\n')
        fout.write('\n'*10)
        word_cnt = sorted([(w,c) for w,c in word_cnt.items()], key = lambda x:x[1], reverse = True)
        for word, cnt in word_cnt:
            fout.write(word + '\t\t' + str(cnt) + '\n')

    print("disease hit icdcode", disease_hit, "disease all", disease_all)
    print(str(int((t2-t1)/60)) + " minutes. " + str(data_count) + " data samples. ")
    return



############### -----------------------------------------##################
########################### Start from here #################################
files= get_files_list()
process_all(files)