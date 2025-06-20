#!/usr/bin/env python
''' Parse a given ccda xml source file.  Produces a limited extract of member data, medication data, and problem data.
    Each of the output types will be appended to the corresponding given file as flat csv.  In the case of multipl medications
    or problems, a new entry line will be created for each.  Each data element will be keyed by the patient identifier.  Each
    row will have a source column to allow easy tracing back to the raw data.
    Parsing discards other common sections (e.g. Care Plan, Chief Complaint, Encounters, Functional Status, Immunizations,
    Declined Immunizations, Patient Instructions, Procedures, Results (Labs), Smoking Status, Vitals)
    Assumes one member per file.  Member file will not filter for duplications.
'''

import os
import sys
import csv
import logging

import xmltodict

from parsers import demographics
from parsers import medications
from parsers import problems

def parse_raw_ccda(source_file: str, members_file: str, medications_file: str, problems_file: str):
    ''' Parse a given ccda xml source file.  Produces a limited extract of member data, medication data, and problem data.
        Each of the output types will be appended to the corresponding given file as flat csv.  In the case of multipl medications
        or problems, a new entry line will be created for each.  Each data element will be keyed by the patient identifier.  Each
        row will have a source column to allow easy tracing back to the raw data.
        Parsing discards other common sections (e.g. Care Plan, Chief Complaint, Encounters, Functional Status, Immunizations,
        Declined Immunizations, Patient Instructions, Procedures, Results (Labs), Smoking Status, Vitals)
        Assumes one member per file.  Member file will not filter for duplications.
    '''
    logging.info('Start parsing %s', source_file)
    with open(source_file, encoding='utf-8') as fh:
        ccda_dict = xmltodict.parse(fh.read())
    member_id, document_id = _extract_info_from_filename(source_file)
    if len(ccda_dict) != 1:
        raise ValueError(f'Multiple member information found in {source_file}')
    demographic_info = demographics.extract_demographic_information_from(ccda_dict, member_id, document_id)
    medication_list = medications.extract_medication_information_from(ccda_dict, member_id, document_id)
    problem_list = problems.extract_problem_information_from(ccda_dict, member_id, document_id)
    _initialize_output_file(members_file, demographics.DEMOGRAPHIC_HEADER)
    _initialize_output_file(medications_file, medications.MEDICATION_HEADER)
    _initialize_output_file(problems_file, problems.PROBLEM_HEADER)
    with open(members_file, 'a', encoding='utf-8') as out_fh:
        csv.writer(out_fh).writerow(demographic_info)
    with open(medications_file, 'a', encoding='utf-8') as out_fh:
        writer = csv.writer(out_fh)
        for row in medication_list:
            writer.writerow(row)
    with open(problems_file, 'a', encoding='utf-8') as out_fh:
        writer = csv.writer(out_fh)
        for row in problem_list:
            writer.writerow(row)
    logging.info('Done parsing %s', source_file)


def _initialize_output_file(filename: str, expected_header: list[str]):
    ''' create the given file and initialize with a header row if it does not already exist
        of verify that the file has the expected schema if it does exit.
    '''
    if os.path.exists(filename):
        with open(filename, encoding='utf-8') as fh:
            header = next(csv.reader(fh))
            if header != expected_header:
                raise ValueError(f'{filename} does not match expected schema')
    else:
        with open(filename, 'w', encoding='utf-8') as out_fh:
            csv.writer(out_fh).writerow(expected_header)


def _extract_info_from_filename(file_name: str) -> tuple[str, str]:
    ''' Extract the member_id and document_id values from the given filename
    '''
    tokens = os.path.splitext(os.path.split(file_name)[-1])
    id_tokens = tokens[0].split('_')
    if tokens[-1] != '.xml' or len(id_tokens) != 3:
        raise ValueError(f'Invalid file name structure: {file_name}')
    return id_tokens[0], id_tokens[1]


if __name__ == '__main__':
    if len(sys.argv) != 5:
        logging.warning('USAGE: %s xml_ccda_source_file members_file medications_file problems_file', sys.argv[0])
        sys.exit(0)

    SOURCE = sys.argv[1]
    MEMBERS = sys.argv[2]
    MEDICATIONS = sys.argv[3]
    PROBLEMS = sys.argv[4]
    if not os.path.exists(SOURCE):
        raise ValueError(f'{SOURCE} does not exist')

    parse_raw_ccda(SOURCE, MEMBERS, MEDICATIONS, PROBLEMS)
