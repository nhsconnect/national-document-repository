# Build test folder for bulk upload

A quick and dirty util script to build a test folder for bulk upload.

The code are located in `test_ingest_pds_data.py` as this originated from parsing the PDS team's test patient data pack.

### Setup

Create a venv and install `boto3`.

### To build a test folder locally

It should generate a random test folder at `output`, with metadata.csv and all pdf files.

The patient data are loaded from csv in `test_patients_data`.

You can control which GP data pack to use, number of patients, number of files for each patient by editing the code.
