
# mkdir -p raw_data

# cd raw_data

# !wget -q https://clinicaltrials.gov/AllPublicXML.zip

# !unzip -q AllPublicXML.zip

# import pandas as pd
# from google.colab import drive
# drive.mount('/content/drive')

import os, csv, pickle
from xml.dom import minidom
from xml.etree import ElementTree as ET
from time import time
import requests
import pandas as pd
from tqdm import tqdm
from utils import walkData, get_files_list

def load_disease2icd():
	disease2icd = dict()
	with open('/content/drive/MyDrive/Mtech /Dissertation/data_output/diseases.csv', 'r') as csvfile:
		rows = list(csv.reader(csvfile, delimiter = ','))[1:]
	for row in rows:
		disease = row[0]
		icd = row[1]
		disease2icd[disease] = icd
	return disease2icd


def get_path_of_all_xml_file():
    raw_data_dir = r"/content/raw_data"
    all_file_paths = []
    for dirpath, _, filenames in os.walk(raw_data_dir):
        file_paths = [os.path.join(dirpath, filename) for filename in filenames]
        all_file_paths.extend(file_paths)
        all_file_paths = [i for i in all_file_paths if "xml" in i]
    return all_file_paths


def check_from_Drug_bank():
    df = pd.read_csv('/content/drive/MyDrive/Mtech /Dissertation/data_output/structure links.csv')
    result_dict = dict(zip(df['Name'], df['SMILES']))
    return result_dict


def drug_hit_smiles(drug, drug2smiles):
    try:
        url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/' +drug + '/property/CanonicalSMILES/TXT'
        smiles = requests.get(url).text.rstrip()
        if 'NotFound' in smiles:
            if drug2smiles[smiles]:
                smiles = drug2smiles[smiles]
            else:
                smiles = None
        else:
            if "\n" in smiles:
                smiles = smiles.split('\n')[0]
            else:
                smiles = smiles
    except:
        smiles = None

    return smiles




def nctid2label_dict():
	nctid2outcome = dict()
	nctid2label = dict()
	with open("/content/drive/MyDrive/Mtech /Dissertation/data_output/outcome2label.txt", 'r') as fin:
		lines = fin.readlines()
		outcome2label = {line.split('\t')[0]:int(line.strip().split('\t')[1]) for line in lines}

	with open("/content/drive/MyDrive/Mtech /Dissertation/data_output/trial_outcomes_v1.csv", 'r') as csvfile:
		csvreader = list(csv.reader(csvfile))[1:]
		nctid2outcome = {row[0]:row[1] for row in csvreader}

	for nctid,outcome in nctid2outcome.items():
		nctid2label[nctid] = outcome2label[outcome]

	return nctid2label

nctid2label = nctid2label_dict()



def xml_file_2_tuple_selection(xml_file):
	tree = ET.parse(xml_file)
	root = tree.getroot()
	nctid = root.find('id_info').find('nct_id').text
	study_type = root.find('study_type').text
	if study_type != 'Interventional':
		return ("non-Interventional",)

	interventions = [i for i in root.findall('intervention')]
	drug_interventions = [i.find('intervention_name').text for i in interventions \
														if i.find('intervention_type').text=='Drug']

	if len(drug_interventions)==0:
		return ("Biological",)

	try:
		status = root.find('overall_status').text
	except:
		status = ''

	try:
		why_stop = root.find('why_stopped').text
	except:
		why_stop = ''


	if nctid not in nctid2label:
		label = -1
	else:
		label = nctid2label[nctid]

	try:
		phase = root.find('phase').text

	except:
		phase = ''
	conditions = [i.text for i in root.findall('condition')]

	try:
		criteria = root.find('eligibility').find('criteria').find('textblock').text
	except:
		criteria = ''

	conditions = [i.lower() for i in conditions]
	drugs = [i.lower() for i in drug_interventions]

	return nctid, status.lower(), why_stop.lower(), label, phase.lower(), conditions, drugs, criteria

def process_all():
    drug2smiles = check_from_Drug_bank()
    disease2icd = load_disease2icd()
    input_file_lst = get_files_list()
    output_file = '/content/sample_data/raw_data.csv'
    t1 = time()
    disease_hit, disease_all, drug_hit, drug_all = 0,0,0,0
    fieldname = ['nctid', 'status', 'why_stop', 'label', 'phase',
                    'diseases', 'icdcodes', 'drugs', 'smiless',
                    'criteria']
    num_noninterventional, num_biologics = 0, 0,
    num_nodrug = 0
    num_nolabel = 0
    num_nodisease = 0
    with open(output_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldname)
        writer.writeheader()
        data_count = 0
        for file in input_file_lst:
            result = xml_file_2_tuple_selection(file)
            if len(result)==1 and result[0] == 'non-Interventional':
                num_noninterventional += 1
                continue
            elif len(result)==1 and result[0]== 'Biological':
                num_biologics += 1
                continue

            nctid, status, why_stop, label, phase, conditions, drugs, criteria = result
            if (label == -1) and ('lack of efficacy' in why_stop or 'efficacy concern' in why_stop or 'accrual' in why_stop):
                label = 0
            if label == -1:
                num_nolabel += 1
                continue


            icdcode_lst = []
            for disease in conditions:
                icdcode = disease2icd[disease] if disease in disease2icd else None
                icdcode_lst.append(icdcode)

            smiles_lst = []
            for drug in drugs:

                smiles = drug_hit_smiles(drug, drug2smiles)
                print(drug, smiles)
                if smiles is not None:

                    smiles_lst.append(smiles)
                else:
                    print("unfounded drug: ", drug)

            if smiles_lst == []:
                num_nodrug += 1
                continue
            icdcode_lst = list(filter(lambda x:x!='None' and x!=None, icdcode_lst))
            if icdcode_lst == []:
                num_nodisease += 1
                continue

            data_count += 1
            writer.writerow({'nctid':nctid, \
                                'status': status, \
                                'why_stop': why_stop, \
                                'label':label, \
                                'phase':phase, \
                                'diseases':conditions, \
                                'icdcodes': icdcode_lst, \
                                'drugs':drugs, \
                                'smiless': smiles_lst, \
                                'criteria':criteria, })
    t2 = time()
    print("disease hit icdcode", disease_hit, "disease all", disease_all, "\n drug hit smiles", drug_hit, "drug all", drug_all)
    print(str(int((t2-t1)/60)) + " minutes. " + str(data_count) + " data samples. ")
    print("number of non-Interventional:", num_noninterventional)
    print("number of Biological:", num_biologics)
    print("number of non-label:", num_nolabel)
    print("number of non-drug", num_nodrug)
    print("number of non-disease", num_nodisease)
    return


def xmlfile_2_date(xml_file):
	tree = ET.parse(xml_file)
	root = tree.getroot()
	try:
		start_date = root.find('start_date').text
	except:
		start_date = ''
	try:
		completion_date = root.find('primary_completion_date').text
	except:
		try:
			completion_date = root.find('completion_date').text
		except:
			completion_date = ''
	return start_date, completion_date

def call_nctid_start_end_date():
    raw_folder = "/content/raw_data"
    nctid_lst = []
    total_num, start_num, completion_num = 0, 0, 0
    with open("/content/drive/MyDrive/Mtech /Dissertation/data_output/raw_data.csv") as fin, open("/content/sample_data/nctid_date.txt", 'w') as fout:
        readers = list(csv.reader(fin))[1:]
        for row in tqdm(readers):
            nctid = row[0]
            file = os.path.join(raw_folder, nctid[:7]+"xxxx/"+nctid+".xml")
            start_date, completion_date = xmlfile_2_date(file)
            if start_date != '':
                start_num += 1
            if completion_date != '':
                completion_num += 1
            total_num += 1
            fout.write(nctid + '\t' + start_date + '\t' + completion_date + '\n')

    print("total_num", total_num)
    print("start_num", start_num)
    print("completion_num", completion_num)

process_all()
call_nctid_start_end_date()