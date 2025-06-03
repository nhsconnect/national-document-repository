import random
from enum import StrEnum
from typing import NamedTuple

from utils.audit_logging_setup import LoggingService

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
NHS_NUMBER = 0000000000

logger = LoggingService(__name__)


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


def pairing_nhs_number_digit(nhs_base: int) -> int:
    nhs_str = str(nhs_base).zfill(9)
    total = sum(int(digit) * weight for digit, weight in zip(nhs_str, range(10, 1, -1)))
    remainder = total % 11
    check_digit = 11 - remainder

    if check_digit == 11 or check_digit == 10:
        return -1
    return check_digit


def generate_nhs_number(nhs_number: int):
    nine_digit_nhs_number = nhs_number // 10

    while True:
        if nine_digit_nhs_number > 999999999:
            logger.info("reached maximum nhs number")
            return nhs_number
        nine_digit_nhs_number = nine_digit_nhs_number + 1
        check_digit = pairing_nhs_number_digit(nine_digit_nhs_number)
        if check_digit >= 0:
            return nhs_number * 10 + check_digit


# 9of20_Lloyd_George_Record_[Brad Edmond Avery]_[9730787212]_[13-09-2006]
def generate_file_name(
    current_file_number: int, number_of_files: int, person_name: str, nhs_number: int
) -> str:
    return (
        f"{current_file_number}of{number_of_files}"
        f"_Lloyd_George_Record_[{person_name}]"
        f"_[{nhs_number}]_[13-09-2006]"
    )


def build_file_path(nhs_number: int, file_name: str) -> str:
    return f"/{nhs_number}/{file_name}"


def create_test_file_names_and_keys(
    number_of_patients: int = 2, number_of_files_for_each_patient: int = 3
):
    # Run this test will generate a random test folder at output
    result = []

    current_patient = 0
    nhs_number = NHS_NUMBER
    while current_patient < number_of_patients:
        current_patient_file = 0
        current_patient_name = generate_random_name()
        while current_patient_file < number_of_files_for_each_patient:
            nhs_number = generate_nhs_number(nhs_number)
            file_name = generate_file_name(
                current_file_number=current_patient_file,
                number_of_files=number_of_files_for_each_patient,
                person_name=current_patient_name,
                nhs_number=nhs_number,
            )
            file_key = build_file_path(nhs_number, current_patient_name)
            result.append((file_name, file_key))
            current_patient_file += 1
        current_patient += 1
    return result


# [(filename, filekey),(filename,filekey)]
# def prepare_test_directory(file_path_list: List[str], metadata_file_content: str):
#     output_folder = "../output"
#     source_pdf_file = "../source_to_copy_from.pdf"
#
#     if os.path.exists(output_folder):
#         shutil.rmtree(output_folder)
#
#     os.mkdir(output_folder)
#     output_folder_path = os.path.abspath(os.path.join(os.getcwd(), output_folder))
#
#     metadata_file_path = os.path.join(output_folder_path, "metadata.csv")
#     with open(metadata_file_path, "w") as f:
#         f.write(metadata_file_content)
#
#     for file_path in file_path_list:
#         if file_path.startswith(tuple(NHS_NUMBER_NO_FILES)):
#             continue
#         output_path = os.path.join(output_folder_path, file_path.lstrip("/"))
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         shutil.copyfile(source_pdf_file, output_path)
