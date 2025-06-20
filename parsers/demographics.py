#!/usr/bin/env python
''' Extract demographic information from the given ccda dictionary and return it as a flat row
'''

import datetime
import logging

from parsers.ccda_segment_codes import SEGMENT_MAP

DEMOGRAPHIC_HEADER = ['MemberID', 'Effective', 'FirstName', 'LastName', 'DOB', 'Gender', 'MaritalStatus', 'Address', 'City',
                      'State', 'Zip', 'Country', 'Phone', 'Language', 'Race', 'Ethnicity', 'Religion',
                      'ProviderName', 'ProviderPhone', 'SourceDocument']

def extract_demographic_information_from(ccda_dict: dict, member_id: str, document_id: str) -> list[str]:
    ''' Extract member information from the document and return as a flat list.
        Ideally validated/populated against https://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.1.1.html
    '''
    record = None
    for val in ccda_dict['ClinicalDocument']['templateId']:
        if val['@root'] in SEGMENT_MAP['demographics']:
            record = ccda_dict['ClinicalDocument']
    if not record:
        raise ValueError('Member information not found')

    demo_list = [None] * len(DEMOGRAPHIC_HEADER)
    demo_list[DEMOGRAPHIC_HEADER.index('MemberID')] = member_id
    demo_list[DEMOGRAPHIC_HEADER.index('Effective')] = _get_effective_date_from(record)
    pr = record['recordTarget']['patientRole']
    patient = pr['patient']
    name = patient['name']
    if isinstance(name, list):
        name = name[0]
    first, last = _get_name(name)
    demo_list[DEMOGRAPHIC_HEADER.index('FirstName')] = first
    demo_list[DEMOGRAPHIC_HEADER.index('LastName')] = last
    demo_list[DEMOGRAPHIC_HEADER.index('DOB')] = _get_birthdate_from(patient)
    demo_list[DEMOGRAPHIC_HEADER.index('Gender')] = patient['administrativeGenderCode']['@code']
    demo_list[DEMOGRAPHIC_HEADER.index('MaritalStatus')] = patient.get('maritalStatusCode', {}).get('@code')
    demo_list[DEMOGRAPHIC_HEADER.index('Race')] = patient['raceCode'].get('@code')
    demo_list[DEMOGRAPHIC_HEADER.index('Ethnicity')] = patient['ethnicGroupCode'].get('@code')
    demo_list[DEMOGRAPHIC_HEADER.index('Religion')] = patient.get('religiousAffiliationCode', {}).get('@code')
    language = patient.get('languageCommunication', {})
    if isinstance(language, list):
        language = language[0]
    demo_list[DEMOGRAPHIC_HEADER.index('Language')] = language.get('languageCode', {}).get('@code')
    addr = pr['addr']
    if isinstance(addr, list):
        addr = addr[0]
    demo_list[DEMOGRAPHIC_HEADER.index('Address')] = addr['streetAddressLine']
    demo_list[DEMOGRAPHIC_HEADER.index('City')] = addr['city']
    demo_list[DEMOGRAPHIC_HEADER.index('State')] = addr['state']
    demo_list[DEMOGRAPHIC_HEADER.index('Zip')] = addr['postalCode']
    demo_list[DEMOGRAPHIC_HEADER.index('Country')] = addr.get('country')
    telecom = pr['telecom']
    if isinstance(telecom, list):
        telecom = telecom[0]
    demo_list[DEMOGRAPHIC_HEADER.index('Phone')] = telecom.get('@value')
    provider = pr.get('providerOrganization', {})
    demo_list[DEMOGRAPHIC_HEADER.index('ProviderName')] = provider.get('name')
    demo_list[DEMOGRAPHIC_HEADER.index('ProviderPhone')] = provider.get('telecom', {}).get('@value')
    demo_list[DEMOGRAPHIC_HEADER.index('SourceDocument')] = document_id
    logging.info('Extracted member information for %s', member_id)
    return demo_list


def _get_name(name: dict) -> tuple:
    ''' extract and return the given name from val.
        several varients to deal with
    '''
    given = name['given']
    if isinstance(given, list):
        given = given[0]
    if not isinstance(given, str):
        given = given.get('#text')
    return given, name['family']


def _get_birthdate_from(patient: dict) -> str:
    ''' extract and return birthdate if it is an integer value
        otherwise None
    '''
    try:
        candidate = patient['birthTime']['@value'][:8]
        return datetime.datetime.strptime(candidate, '%Y%m%d').date().isoformat()
    except:
        return None


def _get_effective_date_from(record: dict) -> str:
    ''' extract and return the effective date from the given record
        otherwise None
    '''
    try:
        candidate = record['effectiveTime']['@value'][:8]
        return datetime.datetime.strptime(candidate, '%Y%m%d').date().isoformat()
    except:
        return None
