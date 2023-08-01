import os
from data_collection import read_xml_file, save_to_csv
# Define the path to the 'raw_data' directory
def get_files_list():
    raw_data_dir = r"F:\Clinical_Trial_Outcome_Prediction\Clinical_Trial_Outcome_Prediction-main\raw_data"

    # Create an empty list to store all the file paths
    all_file_paths = []

    # Use os.walk to traverse through all subdirectories in 'raw_data'
    for dirpath, _, filenames in os.walk(raw_data_dir):
        # Concatenate the directory path with the filenames to get the full file paths
        file_paths = [os.path.join(dirpath, filename) for filename in filenames]
        # Extend the all_file_paths list with the file_paths list for each subdirectory
        all_file_paths.extend(file_paths)
    return all_file_paths
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