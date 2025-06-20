#!/usr/bin/env python
''' Parse each raw ccda xml file in the given folder into the given member, medication, and problem csv files
'''

import os
import sys
import logging

from parse_raw_ccda import parse_raw_ccda

if __name__ == '__main__':
    if len(sys.argv) != 2:
        logging.warning('USAGE: %s xml_source_folder', sys.argv[0])
        sys.exit(0)

    SOURCE = sys.argv[1]
    MEMBER = 'demographic_raw.csv'
    MEDICATION = 'medication.csv'
    PROBLEM = 'problem.csv'
    if not os.path.exists(SOURCE):
        raise ValueError(f'{SOURCE} does not exist')

    for file in os.listdir(SOURCE):
        if file.endswith('_masked.xml'):
            source_file = os.path.join(SOURCE, file)
            parse_raw_ccda(source_file, MEMBER, MEDICATION, PROBLEM)
