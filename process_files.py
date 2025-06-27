#!/usr/bin/env python3
''' Download all files from the AWS URLs in the given file.  If the cache option is specified, the contents
    of each URL will be written to a file of the same name in the local folder or output_folder if given.
    If the process option is specified, the contents of each URL file will be parsed into demographic, medication,
    and problem domains.  Results will be appended to demographic_raw.csv, medicaion.csv, and problem.csv files in
    the local folder or the output_folder if one is given.
'''

import os
import sys
import logging

import requests

from parse_raw_ccda import parse_raw_ccda_text

CACHE_OPTION = 'cache'
PROCESS_OPTION = 'process'

DEMOGRAPHIC_FILE = 'demographic_raw.csv'
MEDICATION_FILE = 'medication.csv'
PROBLEM_FILE = 'problem.csv'

def process_all_files_in(url_file: str, demographic_file: str, medication_file: str, problem_file) -> None:
    ''' Process the file represented by each signed url in the given file into domain specific CSVs in the current folder
        or output folder if given
    '''
    with open(url_file, encoding='utf-8') as fh:
        header = next(fh) #discard header
        if header.startswith('http'):
            raise ValueError(f'header not found in {url_file}')
        for url in fh:
            fname = os.path.split(url.split('?AWSAccessKeyId')[0])[-1]
            logging.info(fname, url)

            try:
                response = requests.get(url, timeout=5)
            except requests.exceptions.Timeout as oops:
                logging.error('Download timeout for %s', url)
                raise oops
            if response.status_code == 200:
                parse_raw_ccda_text(response.text, fname, demographic_file, medication_file, problem_file)
            else:
                raise RuntimeError(f'Download Failed {response.status_code} for {url}')


def download_all_files_in(url_file: str, output_folder: str) -> None:
    ''' Get the contents of all files from the AWS URLs in the given file.  The contents of each URL will be written to
        a file of the same name in the local folder or output_folder if given.
    '''
    with open(url_file, encoding='utf-8') as fh:
        header = next(fh) #discard header
        if header.startswith('http'):
            raise ValueError(f'header not found in {url_file}')
        for url in fh:
            output_file = os.path.join(output_folder, os.path.split(url.split('?AWSAccessKeyId')[0])[-1])
            logging.info(output_file, url)

            try:
                response = requests.get(url, timeout=5)
            except requests.exceptions.Timeout as oops:
                logging.error('Download timeout for %s', url)
                raise oops
            if response.status_code == 200:
                with open(output_file, 'wb') as out_fh:
                    out_fh.write(response.content)
            else:
                raise RuntimeError(f'Download Failed {response.status_code} for {url}')


if __name__ == '__main__':
    USAGE = f'USAGE: {sys.argv[0]} url_file {CACHE_OPTION}|{PROCESS_OPTION} [output_folder]'
    if len(sys.argv) not in (3, 4):
        logging.warning(USAGE)
        sys.exit(0)

    URL_FILE = sys.argv[1]
    if not os.path.exists(URL_FILE):
        raise ValueError(f'{URL_FILE} does not exist')
    OPTION = sys.argv[2].lower()
    OUTPUT_FOLDER = '.'
    if len(sys.argv) == 4:
        OUTPUT_FOLDER = sys.argv[3]
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    if OPTION == CACHE_OPTION:
        download_all_files_in(URL_FILE, OUTPUT_FOLDER)
    elif OPTION == PROCESS_OPTION:
        process_all_files_in(URL_FILE, os.path.join(OUTPUT_FOLDER, DEMOGRAPHIC_FILE),
                             os.path.join(OUTPUT_FOLDER, MEDICATION_FILE), os.path.join(OUTPUT_FOLDER, PROBLEM_FILE))
    else:
        logging.error('Invalid option %s', OPTION)
        logging.error(USAGE)
