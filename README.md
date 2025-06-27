
<div align="center">
  <h1>C-CDA Parsing Eval</h1>
</div>

## Table of Contents
- [Overview](#overview)
- [Scripts](#scripts)
- [Parsers](#parsers)
- [ToDo](#todo)
- [Installation](#installation)
- [License](#license)

## Overview
#### A collection of scripts to download c-cda xml from specified signed URLs and parse them into domain specific CSVs

## Scripts
### process_files.py
#### Download all files from the AWS URLs in the given file.  If the cache option is specified, the contents of each URL will be written to a file of the same name in the local folder or output_folder if given. If the process option is specified, the contents of each URL file will be parsed into demographic, medication, and problem domains.  Results will be appended to demographic_raw.csv, medicaion.csv, and problem.csv files in the local folder or the output_folder if one is given.  Exceptions raised if the get of the URL contents tines out or if the content cannot be downloaded.
```
process_files.py url_file cache|process [output_folder]
```

### bulk_parsing.py
#### Parse each raw ccda xml file in the given folder into the contained demographic, medication, and problem domains. Results will be written to demographic_raw.csv, medicaion.csv, and problem.csv files in the local folder or the output_folder if one is given
```
bulk_parsing.py xml_source_folder [output_folder]
```

### parse_raw_ccda.py
#### Parse a given ccda xml source file.  Produces a limited extract of member data, medication data, and problem data. Each of the output types will be appended to the corresponding given file as flat csv.  In the case of multipl medications or problems, a new entry line will be created for each.  Each data element will be keyed by the patient identifier.  Each row will have a source column to allow easy tracing back to the raw data. Parsing discards other common sections (e.g. Care Plan, Chief Complaint, Encounters, Functional Status, Immunizations, Declined Immunizations, Patient Instructions, Procedures, Results (Labs), Smoking Status, Vitals) Assumes one member per file.  Member file will not filter for duplications.
```
parse_raw_ccda.py xml_ccda_source_file members_file medications_file problems_file
```
#### Two public functions to parse a given file
```
parse_raw_ccda_file(source_file: str, members_file: str, medications_file: str, problems_file: str)
```
#### or parse a given c-cda xml string.
```
parse_raw_ccda_text(source_content: str, source_name: str, members_file: str, medications_file: str, problems_file: str)
```

## Parsers

### parsers/demographics.py
#### helper functions to extract problem data from a given c-cda document dictionary.  returns a list of all problems where columns match the DEMOGRAPHIC_HEADER
```
extract_demographic_information_from(ccda_dict: dict, member_id: str, document_id: str) -> list[str]
```

### parsers/medications.py
#### helper functions to extract medication data from a given c-cda document dictionary.  returns a list of all problems where columns match the MEDICATION_HEADER
```
extract_medication_information_from(ccda_dict: dict, member_id: str, document_id: str) -> list[str]
```

### parsers/problems.py
#### helper functions to extract problem data from a given c-cda document dictionary.  returns a list of all problems where columns match the PROBLEM_HEADER
```
extract_problem_information_from(ccda_dict: dict, member_id: str, document_id: str) -> list[str]
```

### parsers/ccda_segment_codes.py
#### map keyed by c-cda domain and value a list of hl7 segment codes associated with the key

## ToDo
- update existing parsers to pull more data based on hl7.org ccda docs
- add parsers for the reminaing domains (document, allergies, care_plan, chief_complaint, encounters, functional_statuses, immunizations, instructions, results, procedures, social_history, vitals)

## Installation
Install requirements
```
pip install -r requirements.txt
```

## License
Distributed under the MIT License. See [`LICENSE.txt`](LICENSE) for more information.