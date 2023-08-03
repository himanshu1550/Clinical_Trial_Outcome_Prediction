import csv
import xml.etree.ElementTree as ET

def pull_tag_content(root_node, tag_path):
    content_list = []
    stack = [(root_node, '')]

    while stack:
        node, prefix = stack.pop()
        path = prefix + '/' + node.tag

        if path == tag_path and node.text:
            content_list.append(node.text)

        for child in node:
            stack.append((child, path))

    return content_list

def extract_criteria(criteria_textblock):
    # Find the positions of "Inclusion Criteria:" and "Exclusion Criteria:"
    c1 = criteria_textblock.find("Inclusion Criteria:",0)
    c2 = criteria_textblock.find("Exclusion Criteria:",0)

    # Extract the Inclusion Criteria and handle missing criteria
    if c1 >= 0:
        if c2 >= 0:
            inclusion_criteria = criteria_textblock[c1 + len("Inclusion Criteria:"):c2].strip()
        else:
            inclusion_criteria = criteria_textblock[c1 + len("Inclusion Criteria:"):].strip()
    else:
        inclusion_criteria = ""

    # Extract the Exclusion Criteria and handle missing criteria
    if c2 >= 0:
        if c1 >= 0:
            exclusion_criteria = criteria_textblock[c2 + len("Exclusion Criteria:"):].strip()
        else:
            exclusion_criteria = criteria_textblock[c2 + len("Exclusion Criteria:"):].strip()
    else:
        exclusion_criteria = ""
    return inclusion_criteria, exclusion_criteria

def read_xml_file(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        clinical_data = {
            'nct_id': root.findtext('id_info/nct_id',''),
            'brief_title': root.findtext('brief_title',''),
            'official_title': root.findtext('official_title',''),
            'agency': root.findtext('sponsors/lead_sponsor/agency',''),
            'agency_class': root.findtext('sponsors/lead_sponsor/agency_class',''),
            'collaborator_agency': root.findtext('sponsors/collaborator/agency',''),
            'brief_summary': root.findtext('brief_summary/textblock',''),
            'detailed_description': root.findtext('detailed_description/textblock',''),
            # 'conditions': root.findtext('condition',''),
            'overall_status': root.findtext('overall_status',''),
            'phase': root.findtext('phase',''),
            'study_type': root.findtext('study_type',''),
            'has_expanded_access': root.findtext('has_expanded_access',''),
            'intervention': root.findtext('intervention',''),
            'intervention_type': root.findtext('intervention/intervention_type',''),
            'intervention_name': root.findtext('intervention/intervention_name',''),
            'lead_sponsor_agency': root.find('sponsors/lead_sponsor/agency',''),
            'primary_completion_date': root.findtext('primary_completion_date',''),
            'start_date': root.findtext('start_date',''),
            'completion_date': root.findtext('completion_date',''),
            'gender': root.findtext('eligibility/gender',''),
            'minimum_age': root.findtext('eligibility/minimum_age',''),
            'maximum_age': root.findtext('eligibility/maximum_age',''),
            'healthy_volunteers': root.findtext('eligibility/healthy_volunteers',''),
            'why_stopped': root.findtext('why_stopped',''),
        }
        # check for multipal marks
        conditions = pull_tag_content(root, '/clinical_study/condition')
        keywords = pull_tag_content(root, '/clinical_study/keyword')
        clinical_data['conditions'] = conditions
        clinical_data['keywords'] = keywords
        # Extract Inclusion and Exclusion Criteria
        criteria_textblock = root.findtext('eligibility/criteria/textblock','')
        inclusion_criteria, exclusion_criteria = extract_criteria(criteria_textblock)
        clinical_data['inclusion_criteria'] = inclusion_criteria
        clinical_data['exclusion_criteria'] = exclusion_criteria
        return clinical_data

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except ET.ParseError:
        print(f"Error: Invalid XML format in '{file_path}'.")
        return None


def save_to_csv(data_list, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = data_list[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)