# Overview
This project aims to develop a comprehensive clinical trial outcome prediction model to facilitate better decision-making in drug development and treatment planning. The model incorporates a diverse range of drugs and indications (diseases) and provides a holistic understanding of clinical trial outcomes.

## Task 1: Data Collection from ClinicalTrial.gov
In this task, we collected clinical trial records from ClinicalTrial.gov, a primary source containing detailed information about various clinical studies. The data includes NCT IDs, disease names, drugs, trial phases, eligibility criteria, and statistical analysis results. The data was initially in XML format and was converted to CSV for easy processing and analysis.

### Importance:

ClinicalTrial.gov provides a comprehensive repository of clinical trial data, essential for model training and analysis.
Gathering a large dataset allows for a diverse range of clinical scenarios and improves the model's ability to generalize.
Task 2: Standardizing Disease Names with ICD-10 Codes
During this task, we extracted disease names from the data and converted them into standardized ICD-10 codes using the ClinicalTable API. ICD-10 codes provide a common language for recording, reporting, and monitoring diseases, enabling efficient data analysis and classification.

### Importance:

Standardizing disease names allows us to categorize and group clinical trials based on specific diseases.
ICD-10 codes provide a structured and consistent representation of diseases, facilitating data integration and analysis.
Examples:

Diabetes Mellitus, Type 2 --> ICD-10 Codes: ['E11.65', 'E11.9', 'E11.21', 'E11.36', 'E11.41', 'E11.42', 'E11.44']
Breast Cancer --> ICD-10 Codes: ['C79.81', 'D24.1', 'D24.2', 'D24.9', 'D49.3', 'C44.501', 'D48.60']
Asthma --> ICD-10 Codes: ['J45.998', 'J82.83', 'J45.909', 'J45.991', 'J45.20', 'J45.30', 'J45.40']
Task 3: Drug to SMILES Conversion
In this task, we converted drugs into their molecular structures using Simplified Molecular-Input Line-Entry System (SMILES) representations obtained from the DrugBank database. SMILES provide a concise and standardized format for encoding chemical structures, facilitating data integration and similarity analysis.

### Importance:

SMILES representations enable efficient storage, retrieval, and manipulation of molecular structures in computational models.
Calculating drug similarity based on SMILES can help identify potential drug candidates with similar molecular properties.