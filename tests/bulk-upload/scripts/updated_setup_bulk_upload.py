import random
from enum import StrEnum
from typing import NamedTuple

SOURCE_PDF_FILE = "../source_to_copy_from.pdf"

NHS_NUMBER_INVALID_FILE_NAME = []
NHS_NUMBER_INVALID_FILES_NUMBER = []
NHS_NUMBER_INVALID_FILE_NHS_NUMBER = []
NHS_NUMBER_MISSING_FILES = []
NHS_NUMBER_INFECTED = []
NHS_NUMBER_INVALID_PATIENT_NAME = []
NHS_NUMBER_NO_FILES = []
NHS_NUMBER_DUPLICATE_IN_METADATA = []
NHS_NUMBER_WITH_DIFFERENT_UPLOADER = []
NHS_NUMBER_ALREADY_UPLOADED = []
NHS_NUMBER_WRONG_DOB = []
# NHS_number = 0000000001


class Patient(NamedTuple):
    full_name: str
    date_of_birth: str
    nhs_number: str
    ods_code: str


class PatientsDataFile(StrEnum):
    JigginsLane = "ODS_Code_M85143.csv"
    NoOds = "NoODS_ExpiredODS.csv"
    H81109 = "ODS_Code_H81109.csv"
    GPWithAccentCharPatients = "ODS_Code_H85686.csv"
    MockPDS = "ODS_MockPDS.csv"


def generate_random_name():
    first_names = [
        "Alice",
        "Bob",
        "Charlie",
        "Diana",
        "Ethan",
        "Fiona",
        "George",
        "Hannah",
        "Isaac",
        "Julia",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Miller",
        "Davis",
        "Garcia",
        "Martinez",
        "Taylor",
    ]
    first = random.choice(first_names)
    last = random.choice(last_names)
    return f"{first} {last}"


def generate_nhs_number(nhs_number: int):
    while True:
        current_nhs_number = nhs_number + 1
        # if(isvalidNHSNUmber)
        return current_nhs_number + 1


# 9of20_Lloyd_George_Record_[Brad Edmond Avery]_[9730787212]_[13-09-2006]
def generate_file_name(
    current_file_number: int, number_of_files: int, person_name: str
) -> str:
    nhs_number = generate_nhs_number()
    return (
        f"{current_file_number}of{number_of_files}"
        f"_Lloyd_George_Record_[{person_name}]"
        f"_[{nhs_number}]_[13-09-2006]"
    )


def create_test_file_names_and_keys(
    number_of_patients: int = 2, number_of_files_for_each_patient: int = 3
):
    # Run this test will generate a random test folder at output
    # result = []
    # current_patient_name = generate_random_name()
    current_patient = 0
    while current_patient < number_of_patients:
        current_patient_file = 0
        while current_patient_file < number_of_files_for_each_patient:
            # file_name = generate_file_name(
            # current_patient_file,
            # number_of_files_for_each_patient)
            # result.add(current_patient_name,file_key)
            current_patient_file += 1
        current_patient += 1

    # returns [(filename,filekey),
    # (filename,filekey),(filename,filekey)]
    return True
