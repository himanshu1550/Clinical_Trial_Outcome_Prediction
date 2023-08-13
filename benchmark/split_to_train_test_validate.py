import csv
from random import shuffle
from functools import reduce
import pandas as pd


icdcode = "/content/drive/MyDrive/Mtech /Dissertation/"
def rawfile2dict():
	'''
		ccs beta code
	'''
	file = icdcode +  "icdcode/DXCCSR-vs-Beta-CCS-Comparison.xlsx"
	icd2ccs_file = icdcode +  "icdcode/icd2ccs.txt"
	ccscode2description_file =  icdcode +  'icdcode/ccs2description.txt'
	contents = pd.read_excel(open(file, 'rb'), sheet_name = 'ICD-10-CM Code Detail')
	N, _ = contents.shape

	icd10code_lst = contents['ICD-10-CM Code']
	ccs_beta_lst = contents['Beta Version CCS Category']
	ccs_description_lst = contents['Beta Version CCS Category Description']
	icd2ccs = dict()
	ccscode2description = dict()
	for i in range(N):
		icdcode = icd10code_lst[i]
		ccscode = ccs_beta_lst[i]
		ccs_description = ccs_description_lst[i]
		icd2ccs[icdcode] = ccscode
		ccscode2description[ccscode] = ccs_description
	with open(icd2ccs_file, 'w') as fout:
		for k,v in icd2ccs.items():
			fout.write(str(k) + '\t' + str(v) + '\n')
	with open(ccscode2description_file, 'w') as fout:
		for k,v in ccscode2description.items():
			fout.write(str(k) + '\t' + str(v) + '\n')
	return icd2ccs, ccscode2description


def rawfile2dict_CCSR():
	file = icdcode + "icdcode/DXCCSR-vs-Beta-CCS-Comparison.xlsx"
	icd2ccsr_file = icdcode + "icdcode/icd2ccsr.txt"
	contents = pd.read_excel(open(file, 'rb'), sheet_name = 'ICD-10-CM Code Detail')
	N, _ = contents.shape

	icd10code_lst = contents['ICD-10-CM Code']
	ccsr_lst = contents['CCSR1']
	icd2ccsr = dict()
	for i in range(N):
		icdcode = icd10code_lst[i]
		ccsr = ccsr_lst[i][:3]
		icd2ccsr[icdcode] = ccsr
	with open(icd2ccsr_file, 'w') as fout:
		for k,v in icd2ccsr.items():
			fout.write(str(k) + '\t' + str(v) + '\n')
	return icd2ccsr


def file2_icd2ccsr():
	icd2ccsr_file = icdcode + "icdcode/icd2ccsr.txt"
	with open(icd2ccsr_file, 'r') as fin:
		lines = fin.readlines()
	icd2ccsr = {line.split()[0]:line.split()[1] for line in lines}
	return icd2ccsr


def file2_icd2ccs_and_ccs2description():
	icd2ccs = dict()
	icd2ccs_file = icdcode + "icdcode/icd2ccs.txt"
	ccscode2description_file = icdcode + 'icdcode/ccs2description.txt'
	ccscode2description = dict()
	with open(icd2ccs_file, 'r') as fin:
		lines = fin.readlines()
	icd2ccs = {line.split()[0]:line.split()[1] for line in lines}
	with open(ccscode2description_file, 'r') as fin:
		lines = fin.readlines()
	ccscode2description = {line.split()[0]:line.split()[1] for line in lines}
	return icd2ccs, ccscode2description


def cancer_filter_icd10code(icd10code):
	icd2ccs, ccscode2description = file2_icd2ccs_and_ccs2description()
	ccs = icd2ccs[icd10code]
	description = ccscode2description[ccs]
	return 'cancer' in description.lower()

icd2ccsr = file2_icd2ccsr()

def csvfile2rows(input_file):
	with open(input_file, 'r') as csvfile:
		rows = list(csv.reader(csvfile, delimiter = ','))[1:]
	return rows

def filter_phase_I(row):
	if "phase 1" in row[4]:
		return True
	return False

def filter_phase_II(row):
	phase = row[4]
	label = int(row[3])

	if "phase 2" in row[4]:
		return True

	return False

def filter_phase_III(row):
	if "phase 3" in row[4]:
		return True
	return False

def filter_trial(row):
	label = int(row[3])
	if label == 0 and ('phase 1' in row[4] or 'phase 2' in row[4]):
		return True
	if ('phase 3' in row[4] or 'phase 4' in row[4]) and label==1:  ### label == 1
		return True
	return False

def icdcode_text_2_lst_of_lst(text):
	text = text[2:-2]
	lst_lst = []
	for i in text.split('", "'):
		i = i[1:-1]
		lst_lst.append([j.strip()[1:-1] for j in i.split(',')])
	return lst_lst

def row2icdcodelst(row):
	icdcode_text = row[6]
	icdcode_lst2 = icdcode_text_2_lst_of_lst(icdcode_text)
	icdcode_lst = reduce(lambda x,y:x+y, icdcode_lst2)
	icdcode_lst = [i.replace('.', '') for i in icdcode_lst]
	return icdcode_lst


def filter_nervous(row):
	icdcode_lst = row2icdcodelst(row)
	for icdcode in icdcode_lst:
		try:
			ccsr = icd2ccsr[icdcode]
			if ccsr == 'NVS':
				return True
		except:
			pass
	return False

def filter_cancer(row):
	icdcode_lst = row2icdcodelst(row)
	for icdcode in icdcode_lst:
		try:
			ccsr = icd2ccsr[icdcode]
			if ccsr == 'NEO':
				return True
		except:
			pass
	return False

def filter_infect(row):
	icdcode_lst = row2icdcodelst(row)
	for icdcode in icdcode_lst:
		try:
			ccsr = icd2ccsr[icdcode]
			if ccsr == 'INF':
				return True
		except:
			pass
	return False


def filter_respiratory(row):
	icdcode_lst = row2icdcodelst(row)
	for icdcode in icdcode_lst:
		try:
			ccsr = icd2ccsr[icdcode]
			if ccsr == 'RSP':
				return True
		except:
			pass
	return False

def filter_digest(row):
	icdcode_lst = row2icdcodelst(row)
	for icdcode in icdcode_lst:
		try:
			ccsr = icd2ccsr[icdcode]
			if ccsr == 'DIG':
				return True
		except:
			pass
	return False




def write_row_to_csvfile(rows, fieldname, output_file):
	with open(output_file, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldname)
		writer.writeheader()
		for row in rows:
			dic = {k:row[i] for i,k in enumerate(fieldname)}
			writer.writerow(dic)
	return


nctid2year = dict()
with open(icdcode + 'data_output/nctid_date.txt', 'r') as fin:
	lines = fin.readlines()
for line in lines:
	nctid, start_year, completion_year = line.strip('\n').split('\t')
	start_year = 0 if start_year=='' else int(start_year.split()[-1])
	completion_year = 0 if completion_year == '' else int(completion_year.split()[-1])
	nctid2year[nctid] = start_year, completion_year  #### 0, 2018

def row2year(row):
	nctid = row[0]
	start_year, completion_year = nctid2year[nctid]
	return start_year, completion_year


def split_data(rows, split_year):
	learn_row = []
	test_row = []
	for row in rows:
		start_year, completion_year = row2year(row)
		if 0 < completion_year < split_year:
			learn_row.append(row)
		elif 0 < start_year and start_year >= split_year:
			test_row.append(row)
	shuffle(learn_row)
	n = len(learn_row)
	train_num = int(n*0.9)
	train_row = learn_row[:train_num]
	valid_row = learn_row[train_num:]

	return train_row, valid_row, test_row


def check_pos_and_neg(rows):
	pos_cnt, neg_cnt = 0, 0
	for row in rows:
		if int(row[3])==1:
			pos_cnt += 1
		elif int(row[3])==0:
			neg_cnt += 1
	print("pos: ", pos_cnt, " neg:", neg_cnt)

def select_and_split_data(input_file, filter_func, output_file_name, split_year=2014):
	rows = csvfile2rows(input_file)
	rows = list(filter(filter_func, rows))
	# shuffle(rows)
	positive_num = len(list(filter(lambda x:int(x[3])==1, rows)))
	negative_num = len(rows) - positive_num
	print("\t\tpos =", str(positive_num), "  neg =", str(negative_num))
	train_row, valid_row, test_row = split_data(rows, split_year)
	fieldname = ['nctid', 'status', 'why_stop', 'label', 'phase',
				 'diseases', 'icdcodes', 'drugs', 'smiless', 'criteria']

	print("train")
	check_pos_and_neg(train_row)
	print("valid")
	check_pos_and_neg(valid_row)
	print("test")
	check_pos_and_neg(test_row)
	output_file = output_file_name.replace('.csv', '_train.csv')
	write_row_to_csvfile(train_row, fieldname, output_file)
	output_file = output_file_name.replace('.csv', '_valid.csv')
	write_row_to_csvfile(valid_row, fieldname, output_file)
	output_file = output_file_name.replace('.csv', '_test.csv')
	write_row_to_csvfile(test_row, fieldname, output_file)

	subset_test_row = list(filter(filter_respiratory, test_row))
	output_file = output_file_name.replace('.csv', '_respiratory_test.csv')
	write_row_to_csvfile(subset_test_row, fieldname, output_file)

	subset_test_row = list(filter(filter_infect, test_row))
	output_file = output_file_name.replace('.csv', '_infection_test.csv')
	write_row_to_csvfile(subset_test_row, fieldname, output_file)

	subset_test_row = list(filter(filter_nervous, test_row))
	output_file = output_file_name.replace('.csv', '_nervous_test.csv')
	write_row_to_csvfile(subset_test_row, fieldname, output_file)

	subset_test_row = list(filter(filter_digest, test_row))
	output_file = output_file_name.replace('.csv', '_digest_test.csv')
	write_row_to_csvfile(subset_test_row, fieldname, output_file)

	subset_test_row = list(filter(filter_cancer, test_row))
	output_file = output_file_name.replace('.csv', '_cancer_test.csv')
	write_row_to_csvfile(subset_test_row, fieldname, output_file)

	return


def smiles_txt_to_lst(text):
	"""
		"['CN[C@H]1CC[C@@H](C2=CC(Cl)=C(Cl)C=C2)C2=CC=CC=C12', 'CNCCC=C1C2=CC=CC=C2CCC2=CC=CC=C12']"
	"""
	text = text[1:-1]
	lst = [i.strip()[1:-1] for i in text.split(',')]
	return lst

from copy import deepcopy

def clean_data(input_file, clean_file):

	rows = csvfile2rows(input_file)
	newrows = []
	fieldname = ['nctid','status','why_stop','label','phase','diseases','icdcodes','drugs','smiless','criteria']
	with open(clean_file, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldname)
		writer.writeheader()
		for row in rows:
			smiless = row[8]
			if '[O--].[Mg++]' in smiless:
				smiles_lst = smiles_txt_to_lst(smiless)
				smiles_lst = set(smiles_lst)
				smiles_lst.remove('[O--].[Mg++]')
				if len(smiles_lst)==0:
					continue
				smiles_lst = str(list(smiles_lst))
				newrow = row[:8] + [smiles_lst] + row[9:]
			else:
				newrow = row

			dic = {k:newrow[i] for i,k in enumerate(fieldname)}
			writer.writerow(dic)
	return



if __name__ == "__main__":
	input_file = '/content/drive/MyDrive/Mtech /Dissertation/data_output/raw_data.csv'
	clean_file = "/content/drive/MyDrive/Mtech /Dissertation/data_output/clean_data.csv"

	clean_data(input_file, clean_file)
	print("------------ phase I -------------")
	select_and_split_data(clean_file, filter_phase_I, 'data/phase_I.csv')
	print("----------- phase II -------------")
	select_and_split_data(clean_file, filter_phase_II, 'data/phase_II.csv')
	print("----------- phase III ----------")
	select_and_split_data(clean_file, filter_phase_III, 'data/phase_III.csv')
	print("----------- indication ----------")
	select_and_split_data(clean_file, filter_trial, 'data/indication.csv')
