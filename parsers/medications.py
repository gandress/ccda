#!/usr/bin/env python
''' Extract medication information from the given ccda dictionary and return it as a list of
    flat rows, one per medication found.
'''

import datetime
import logging

from parsers.ccda_segment_codes import SEGMENT_MAP

MEDICATION_HEADER = ['MemberID', 'StartDate', 'EndDate', 'Status', 'ProductCode', 'ProductCodeSystem', 'ProductText',
                     'ProductTranslationCode', 'ProductTranslationCodeSystem', 'ProductTranslationCodeSystemName',
                     'DoseQuantityValue', 'DoseQuantityUnit', 'PreconditionCode', 'PreconditionCodeSystem', 'RouteName', 'RouteCode',
                     'RouteCodeSystem', 'RouteCodeSystemName', 'SourceDocument']

def extract_medication_information_from(ccda_dict: dict, member_id: str, document_id: str) -> list[str]:
    ''' Extract medication information from the document and return as a list with one row per medication.
        Ideally validated/populated against https://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.2.1.html and
        https://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.2.1.1.html
    '''
    medications = []
    medication_section = None
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
            if id_val['@root'] in SEGMENT_MAP['medications']:
                if 'entry' in val['section']:
                    medication_section = val['section']
                else:
                    logging.info('No medication entries found')
                    return medications
                break
        if medication_section is not None:
            break
    if medication_section is None:
        raise ValueError('No Medication section found')

    entry_vals = medication_section['entry']
    if not isinstance(entry_vals, list):
        entry_vals = [entry_vals]
    for entry in entry_vals:
        medications.append(_get_medication_data_from(entry, member_id, document_id))
    logging.info('Extracted medication information for %s', member_id)
    return medications


def _get_medication_data_from(entry: dict, member_id: str, document_id: str) -> list[str]:
    ''' create and return a list representation of the given entry dictionary
    '''
    record = entry['substanceAdministration']
    medication_list = [None] * len(MEDICATION_HEADER)
    medication_list[MEDICATION_HEADER.index('MemberID')] = member_id
    start, end = _extract_date_range_from(record)
    medication_list[MEDICATION_HEADER.index('StartDate')] = start
    medication_list[MEDICATION_HEADER.index('EndDate')] = end
    medication_list[MEDICATION_HEADER.index('Status')] = record.get('statusCode', {}).get('@code')
    medication_list[MEDICATION_HEADER.index('ProductCode')] = record['consumable']['manufacturedProduct']['manufacturedMaterial']['code'].get('@code')
    medication_list[MEDICATION_HEADER.index('ProductCodeSystem')] = record['consumable']['manufacturedProduct']['manufacturedMaterial']['code'].get('@codeSystem')
    t_code, t_code_system, t_code_system_name = _get_product_translation_info_from(record)
    medication_list[MEDICATION_HEADER.index('ProductTranslationCode')] = t_code
    medication_list[MEDICATION_HEADER.index('ProductTranslationCodeSystem')] = t_code_system
    medication_list[MEDICATION_HEADER.index('ProductTranslationCodeSystemName')] = t_code_system_name
    medication_list[MEDICATION_HEADER.index('DoseQuantityValue')] = record.get('doseQuantity', {}).get('@value')
    medication_list[MEDICATION_HEADER.index('DoseQuantityUnit')] = record.get('doseQuantity', {}).get('@unit')
    pc_code, pc_code_system = _get_precondition_info_from(record)
    medication_list[MEDICATION_HEADER.index('PreconditionCode')] = pc_code
    medication_list[MEDICATION_HEADER.index('PreconditionCodeSystem')] = pc_code_system
    medication_list[MEDICATION_HEADER.index('RouteName')] = record.get('routeCode', {}).get('@displayName')
    medication_list[MEDICATION_HEADER.index('RouteCode')] = record.get('routeCode', {}).get('@code')
    medication_list[MEDICATION_HEADER.index('RouteCodeSystem')] = record.get('routeCode', {}).get('@codeSystem')
    medication_list[MEDICATION_HEADER.index('RouteCodeSystemName')] = record.get('routeCode', {}).get('@codeSystemName')
    medication_list[MEDICATION_HEADER.index('SourceDocument')] = document_id
    return medication_list


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


def _get_product_translation_info_from(record: dict) -> tuple:
    ''' extract and return product translation information from the given entry.
        return a tuple of none if none exist
    '''
    translation = record['consumable']['manufacturedProduct']['manufacturedMaterial']['code'].get('translation', {})
    if isinstance(translation, list):
        translation = translation[0]
    code = translation.get('@code')
    code_system = translation.get('@codeSystem')
    code_system_name = translation.get('@codeSystemName')
    return code, code_system, code_system_name


def _get_precondition_info_from(record: dict) -> tuple:
    ''' extract and return precondition information from the given entry.
        return a tuple of none if none exist
    '''
    code = None
    code_system = None
    if 'precondition' in record:
        precondition = record['precondition']
        if isinstance(precondition, list):
            precondition = precondition[0]
        code = precondition['criterion']['code']['@code']
        code_system = precondition['criterion']['code']['@codeSystem']
    return code, code_system
