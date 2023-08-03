###### import ######
import numpy as np
try:
	from rdkit import Chem 
	from rdkit.Chem import AllChem
except:
	pass 
###### import ######


### tricky
def normalize_disease(name):
    name = name.lower()
    if 'lymphoma' in name:
      return 'lymphoma'
    name = name.replace(',', '')
    name = name.replace('(', ' ')
    name = name.replace(')', ' ')

    name = name.replace('cancer', 'neoplasm')
    name = name.replace('neoplasms', 'neoplasm')
    name = name.replace('tumors', 'tumor')

    name = name.replace('infections', 'infection')
    name = name.replace('diseases', 'disease')
    name = name.replace('disorders', 'disorder')
    name = name.replace('syndromes', 'syndrome')

    name = ' '.join(name.split())
    if name.split()[0]=='stage':
      name = ' '.join(name.split()[2:])

    name_lst = [name]
    if ' neoplasm' in name:
      # print(name)
      name_lst.append(name.replace('neoplasm', 'tumor'))
      name_split = name.split()
      idx = name_split.index('neoplasm')
      name2 = name_split[idx-1] + ' ' + name_split[idx]
      name_lst.append(name2)
    if ' tumor' in name:
      name_lst.append(name.replace('tumor', 'neoplasm'))
      name_split = name.split()
      idx = name_split.index('tumor')
      name2 = name_split[idx-1] + ' ' + name_split[idx]
      name_lst.append(name2)
    if 'disease' in name:
      name_lst.append(name.replace('disease', '').strip())
    if 'disorder' in name:
      name_lst.append(name.replace('disorder', '').strip())
    if '-related' in name:
      name_lst.append(name.replace('-related', '').strip())
    if 'syndrome' in name:
      name_lst.append(name.replace('syndrome', '').strip())


    if 'lung' in name and 'carcinoma' in name:
      name_lst.append('lung carcinoma')
    elif 'cell' in name and 'carcinoma' in name:
      name_lst.append('cell carcinoma')
    elif 'carcinoma' in name:
      name_lst.append('carcinoma')



    ## approximation 1	very few
    organ = ['liver', 'kidney', 'cardio', 'renal', 'hiv']
    for word in organ:
      if word in name:
        name_lst.append(word)

    # approximation 2 most 20%
    word_lst = sorted([(word, len(word)) for word in name.split()], key = lambda x:x[1], reverse = True)
    for word, cnt in word_lst:
      if cnt < 8:
        break
      name_lst.append(word)

    return name_lst








def get_icd_from_nih(name):
    prefix = 'https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search?sf=code,name&terms='
    name_lst = normalize_disease(name)
    for name in name_lst:
        url = prefix + name
        response = requests.get(url)
        text = response.text
        if text == '[0,[],null,[]]':
          continue
        text = text[1:-1]
        idx1 = text.find('[')
        idx2 = text.find(']')
        codes = text[idx1+1:idx2].split(',')
        codes = [i[1:-1] for i in codes]
        return codes
    return None

def walkData(root_node, prefix, result_list):

    temp_list = [prefix + '/' + root_node.tag, root_node.text]
    result_list.append(temp_list)

    for child in root_node:
        walkData(child, prefix=prefix + '/' + root_node.tag, result_list=result_list)



def root2outcome(root):
    result_list = []
    walkData(root, prefix = '', result_list = result_list)
    filter_func = lambda x:'p_value' in x[0]
    outcome_list = list(filter(filter_func, result_list))
    if len(outcome_list)==0:
      return None
    outcome = outcome_list[0][1]
    if outcome[0]=='<':
      return 1
    if outcome[0]=='>':
      return 0
    if outcome[0]=='=':
      outcome = outcome[1:]
    try:
      label = float(outcome)
      if label < 0.05:
        return 1
      else:
        return 0
    except:
      return None
