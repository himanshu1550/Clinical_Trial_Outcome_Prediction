from google.colab import drive
drive.mount('/content/drive')
import pandas as pd
import requests
from time import time
import os

# Read the full data
def retrive_smiles_from_drug(input_file, dir_path):
    df = pd.read_csv(input_file)

    # Filter the DataFrame for 'intervention_type' == 'Drug'
    data = df[df['intervention_type'] == 'Drug']

    # Process and save the results in batches
    chunk_size = 5000
    num_batches = (len(data) + chunk_size - 1) // chunk_size  # Calculate the number of batches
    output_directory = dir_path
    timestamp = int(time())
    start_iteration = 9
    try:
        for i in range(start_iteration, num_batches):
            if i==12:
                break

            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size

            # Extract the chunk to process
            chunk = data.iloc[start_idx:end_idx]

            smiles_df = pd.DataFrame(columns=['Name', 'Smiles'])

            for x in chunk.index:
                ntc_id = chunk['nct_id'][x]
                try:
                    url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/' + chunk['intervention_name'][x] + '/property/CanonicalSMILES/TXT'
                    # remove new line character with rstrip
                    smiles = requests.get(url).text.rstrip()
                    if 'NotFound' in smiles:
                        smiles_df = smiles_df.append({'Name': ntc_id, 'Smiles': "not found"}, ignore_index=True)
                    else:
                        smiles_df = smiles_df.append({'Name': ntc_id, 'Smiles': smiles}, ignore_index=True)
                except:
                    smiles_df = smiles_df.append({'Name': ntc_id, 'Smiles': "not found"}, ignore_index=True)

            # Save the processed chunk to the output file with a unique name
            output_file = f'{output_directory}smiles_chunk_{timestamp}_{i}.csv'
            smiles_df.to_csv(output_file, index=False)
        return True
    except Exception as e:
        print(e)
        return False

def combine_all_csv(dir_path, output_file_path):
    try:
        files_in_directory = os.listdir(dir_path)
        csv_files = [file for file in files_in_directory if file.endswith('.csv') and file.startswith('smiles')]
        dataframes = []
        for file in csv_files:
            file_path = os.path.join(dir_path, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)

        merged_df = pd.concat(dataframes, ignore_index=True)
        merged_df.duplicated().any()

        combined_df = df.merge(merged_df, left_on='nct_id', right_on='Name', how='left')
        combined_df.drop('Name', axis=1, inplace=True)
        combined_df.to_csv(output_file_path)
        return os.path.exists(output_file_path)
    except Exception as e:
        print(e)
        return False


input_combined_file = '/content/drive/MyDrive/Mtech /Dissertation/data_output/combine_output.csv'
output_file_path = '/content/drive/MyDrive/Mtech /Dissertation/data_output/combine_output_with_smiles.csv'
dir = '/content/drive/MyDrive/Mtech /Dissertation/data_output/'
response = retrive_smiles_from_drug(input_combined_file, dir)
if response:
    if_saved = combine_all_csv(dir,output_file_path)
    if if_saved:
        print("file is saved to location")
    else:
        print("Error while saving the file....")
else:
    print("Error.....................")