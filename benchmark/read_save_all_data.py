import os
from data_collection import read_xml_file, save_to_csv
from utils import get_files_list
# Define the path to the 'raw_data' directory

# Now, all_file_paths contains the paths of all the files in the 'raw_data' directory and its subdirectories
def call_all_files_and_extract():
    data_list = []
    csv_file = r"../data/file_output.csv"
    for file_path in get_files_list()[:5]:
        if file_path.endswith(".xml"):
            clinical_data = read_xml_file(file_path)
            if clinical_data is not None:
                data_list.append(clinical_data)

    if data_list:
        save_to_csv(data_list, csv_file)
        print(f"Data from {len(data_list)} XML files saved to '{csv_file}' successfully.")
    else:
        print("No valid data found in XML files.")