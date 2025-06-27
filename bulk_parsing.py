#!/usr/bin/env python
''' Parse each raw ccda xml file in the given folder into the contained demographic, medication, and problem
    domains. Results will be written to demographic_raw.csv, medicaion.csv, and problem.csv files in the local
    folder or the output_folder if one is given
'''

import os
import sys
import logging

from parse_raw_ccda import parse_raw_ccda_file

if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        logging.warning('USAGE: %s xml_source_folder [output_folder]', sys.argv[0])
        sys.exit(0)

    SOURCE = sys.argv[1]
    if not os.path.exists(SOURCE):
        raise ValueError(f'{SOURCE} does not exist')
    OUTPUT_FOLDER = '.'
    if len(sys.argv) == 3:
        OUTPUT_FOLDER = sys.argv[2]
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    DEMOGRAPHIC_FILE = 'demographic_raw.csv'
    MEDICATION_FILE = 'medication.csv'
    PROBLEM_FILE = 'problem.csv'

    for file in os.listdir(SOURCE):
        if file.endswith('_masked.xml'):
            source_file = os.path.join(SOURCE, file)
            parse_raw_ccda_file(source_file, os.path.join(OUTPUT_FOLDER, DEMOGRAPHIC_FILE),
                                os.path.join(OUTPUT_FOLDER, MEDICATION_FILE), os.path.join(OUTPUT_FOLDER, PROBLEM_FILE))
