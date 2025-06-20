#!/usr/bin/env python
''' Extract problem information from the given ccda dictionary and return it as a list of
    flat rows, one per problem found.
'''

import datetime
import logging

from parsers.ccda_segment_codes import SEGMENT_MAP

PROBLEM_HEADER = ['MemberID', 'StartDate', 'EndDate', 'Status', 'Code', 'CodeSystem', 'CodeSystemName',
                  'ObservationCode', 'ObservationCodeSystem', 'ObservationCodeSystemName',
                  'TranslationCode', 'TranslationCodeSystem', 'TranslationCodeSystemName', 'SourceDocument']

def extract_problem_information_from(ccda_dict: dict, member_id: str, document_id: str) -> list[str]:
    ''' Extract problem information from the document and return as a list with one row per problem.
        Ideally validated/populated against https://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.2.5.html and
        https://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.2.5.1.html
    '''
    problems = []
    problems_section = None
    component_list = ccda_dict['ClinicalDocument']['component']['structuredBody']['component']
    for val in component_list:
        if 'templateId' not in val['section']:
            continue
        if isinstance(val['section']['templateId'], list):
            ids = val['section']['templateId']
        elif isinstance(val['section']['templateId'], dict):
            ids = [val['section']['templateId']]
        else:
            raise ValueError('Invalid templateId structure')
        for id_val in ids:
            if id_val['@root'] in SEGMENT_MAP['problems']:
                if 'entry' in val['section']:
                    problems_section = val['section']
                else:
                    logging.info('No problem entries found')
                    return problems
                break
        if problems_section is not None:
            break
    if problems_section is None:
        raise ValueError('No Problem section found')

    entry_vals = problems_section['entry']
    if not isinstance(entry_vals, list):
        entry_vals = [entry_vals]
    for entry in entry_vals:
        problems.append(_get_problem_data_from(entry, member_id, document_id))
    logging.info('Extracted problem information for %s', member_id)
    return problems


def _get_problem_data_from(entry: dict, member_id: str, document_id: str) -> list[str]:
    ''' create and return a list representation of the given entry dictionary
    '''
    record = entry['act']
    problem_list = [None] * len(PROBLEM_HEADER)
    problem_list[PROBLEM_HEADER.index('MemberID')] = member_id
    start, end = _extract_date_range_from(record)
    problem_list[PROBLEM_HEADER.index('StartDate')] = start
    problem_list[PROBLEM_HEADER.index('EndDate')] = end
    problem_list[PROBLEM_HEADER.index('Status')] = record['statusCode'].get('@code')
    problem_list[PROBLEM_HEADER.index('Code')] = record['code']['@code']
    problem_list[PROBLEM_HEADER.index('CodeSystem')] = record['code']['@codeSystem']
    problem_list[PROBLEM_HEADER.index('CodeSystemName')] = record['code'].get('@codeSystemName')
    relationship = record['entryRelationship']
    if isinstance(relationship, list):
        relationship = relationship[0]
    value = relationship['observation']
    problem_list[PROBLEM_HEADER.index('ObservationCode')] = value['code']['@code']
    problem_list[PROBLEM_HEADER.index('ObservationCodeSystem')] = value['code']['@codeSystem']
    problem_list[PROBLEM_HEADER.index('ObservationCodeSystemName')] = value['code'].get('@codeSystemName')
    translation = value['code'].get('translation')
    if translation:
        problem_list[PROBLEM_HEADER.index('TranslationCode')] = translation['@code']
        problem_list[PROBLEM_HEADER.index('TranslationCodeSystem')] = translation['@codeSystem']
        problem_list[PROBLEM_HEADER.index('TranslationCodeSystemName')] = translation['@codeSystemName']
    problem_list[PROBLEM_HEADER.index('SourceDocument')] = document_id
    return problem_list


def _extract_date_range_from(entry: dict) -> tuple:
    ''' extract and return start and end date information from the given record.
        return a tuple of none if none exist
    '''
    start = None
    end = None
    time_extract = entry.get('effectiveTime')
    if time_extract:
        if isinstance(time_extract, list):
            time_extract = time_extract[0]
        if 'low' in time_extract:
            try:
                start_candidate = time_extract['low']['@value'][:8]
                start = datetime.datetime.strptime(start_candidate, '%Y%m%d').date().isoformat()
            except:
                start = None
        if 'high' in time_extract:
            try:
                end_candidate = time_extract['high']['@value'][:8]
                end = datetime.datetime.strptime(end_candidate, '%Y%m%d').date().isoformat()
            except:
                end = None
    return start, end
