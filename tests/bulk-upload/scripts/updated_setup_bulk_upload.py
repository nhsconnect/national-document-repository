import argparse
import random
from enum import StrEnum
from typing import NamedTuple

import boto3

SOURCE_PDF_FILE_NAME = "source_to_copy_from.pdf"
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
NHS_NUMBER = "0000000000"


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
    nhs_base = str(nhs_base).zfill(9)
    total = sum(
        int(digit) * weight for digit, weight in zip(nhs_base, range(10, 1, -1))
    )
    remainder = total % 11
    check_digit = 11 - remainder

    if check_digit == 11 or check_digit == 10:
        return -1
    return check_digit


def generate_nhs_number(nhs_number: str):
    nine_digit_nhs_number = int(nhs_number[:-1].zfill(9))

    while nine_digit_nhs_number <= 999999999:
        nine_digit_nhs_number += 1
        check_digit = pairing_nhs_number_digit(nine_digit_nhs_number)
        if check_digit >= 0:
            return f"{nine_digit_nhs_number}{check_digit}".zfill(10)
    return nhs_number


# 9of20_Lloyd_George_Record_[Brad Edmond Avery]_[9730787212]_[13-09-2006]
def generate_file_name(
    current_file_number: int, number_of_files: int, person_name: str, nhs_number: str
) -> str:
    return (
        f"{current_file_number}of{number_of_files}"
        f"_Lloyd_George_Record_[{person_name}]"
        f"_[{nhs_number}]_[13-09-2006]"
    )


def build_file_path(nhs_number: str, file_name: str) -> str:
    return f"{nhs_number}/{file_name}"


def create_test_file_keys(
    requested_patients_number: int = 2, number_of_files_for_each_patient: int = 3
):
    result = []
    nhs_number = NHS_NUMBER

    for _ in range(requested_patients_number):
        patient_name = generate_random_name()
        nhs_number = generate_nhs_number(nhs_number)

        for file_num in range(1, number_of_files_for_each_patient + 1):
            file_name = generate_file_name(
                current_file_number=file_num,
                number_of_files=number_of_files_for_each_patient,
                person_name=patient_name,
                nhs_number=nhs_number,
            )
            file_key = build_file_path(nhs_number, file_name)
            result.append(file_key)
    return result


def copy_to_s3(file_names_and_keys: list[tuple[str, str]], source_file_key: str):
    # Copy
    client = boto3.client("s3")
    for file_name, file_key in file_names_and_keys:
        client.copy_object(
            Bucket=STAGING_BUCKET,
            Key=file_key,
            CopySource={"Bucket": STAGING_BUCKET, "Key": source_file_key},
            StorageClass="INTELLIGENT_TIERING",
        )

    # Rename subsequent patient records


def upload_source_file_to_staging(file_name: str, file_key: str):
    # this one is a bit flaky
    client = boto3.client("s3")
    client.upload_file(
        Filename=file_name,
        Bucket=STAGING_BUCKET,
        Key=file_key,
        ExtraArgs={"StorageClass": "INTELLIGENT_TIERING"},
    )

    scan_result = "Clean"
    client.put_object_tagging(
        Bucket=STAGING_BUCKET,
        Key=file_key,
        Tagging={
            "TagSet": [
                {"Key": "scan-result", "Value": scan_result},
                {"Key": "date-scanned", "Value": "2023-11-14T21:10:33Z"},
            ]
        },
    )


def upload_lg_files_to_staging(lg_file_keys: list[str], source_pdf_file_key):
    # this one is a bit flaky
    client = boto3.client("s3")
    for target_file_key in lg_file_keys:
        client.copy_object(
            CopySource={"Bucket": STAGING_BUCKET, "Key": source_pdf_file_key},
            Bucket=STAGING_BUCKET,
            Key=target_file_key,
            StorageClass="INTELLIGENT_TIERING",
            MetadataDirective="COPY",
        )

        scan_result = "Clean"
        client.put_object_tagging(
            Bucket=STAGING_BUCKET,
            Key=target_file_key,
            Tagging={
                "TagSet": [
                    {"Key": "scan-result", "Value": scan_result},
                    {"Key": "date-scanned", "Value": "2023-11-14T21:10:33Z"},
                ]
            },
        )


def check_confirmation(confirmation: str):
    if confirmation in ["Y", "y", "Yes", "YES"]:
        return True
    return False


def get_user_input():
    parser = argparse.ArgumentParser(description="Test setup script arguments.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to run the script on.",
    )
    parser.add_argument(
        "--delete-table",
        action="store_true",
        help="Remove all existing data from the dynamo tables.",
    )
    parser.add_argument(
        "--download-data",
        action="store_true",
        help="Download the Test Data Files from S3",
    )
    parser.add_argument(
        "--build-files", action="store_true", help="Build the test files."
    )
    parser.add_argument("--num-patients", help="Amount of patients to create")
    parser.add_argument("--num-files", help="Number of files per patient to build.")
    parser.add_argument(
        "--empty-lloydgeorge-store",
        action="store_true",
        help="Remove all files from the LloydGeorge Record Buckets",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload the test files to S3 and add the virus-scan tag.",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_user_input()
    print("Welcome to test set up script")
    ENVIRONMENT = args.environment or input(
        "Please enter the environment you want to use:"
    )
    STAGING_BUCKET = f"{ENVIRONMENT}-staging-bulk-store"
    LLOYD_GEORGE_BUCKET = f"{ENVIRONMENT}-lloyd-george-store"
    BULK_UPLOAD_TABLE_NAME = f"{ENVIRONMENT}_BulkUploadReport"
    LG_TABLE_NAME = f"{ENVIRONMENT}_LloydGeorgeReferenceMetadata"

    if not args.environment:
        env_confirmation = input(
            f"Please confirm you want to use {ENVIRONMENT} (y/N): "
        )
        if not check_confirmation(env_confirmation):
            print("Exiting Script")
            exit(0)

    # if (
    #         args.delete_table
    #         or input(
    #     "Would you like to remove all existing data from the dynamo tables? (y/N) "
    # ).lower()
    #         == "y"
    # ):
    #     removing_previous_uploads()

    number_of_patients = args.num_patients or int(
        input("How many patients do you wish to generate")
    )

    file_number = args.num_files or int(
        input("How many files per patient do you wish to generate: ")
    )
    file_keys = create_test_file_keys(int(number_of_patients), int(file_number))

    if (
        args.upload
        or input(
            "Would you like to upload the test files to S3 "
            "and add the virus-scan tag? (y/N) "
        ).lower()
        == "y"
    ):
        # fileKeys = [
        #     (SOURCE_PDF_FILE, SOURCE_PDF_FILE_NAME),
        #     # (source_file_name, SOURCE_PDF_FILE_NAME),
        # ]
        upload_source_file_to_staging(SOURCE_PDF_FILE, SOURCE_PDF_FILE_NAME)

        upload_lg_files_to_staging(file_keys, SOURCE_PDF_FILE_NAME)
    # if (
    #     args.empty_lloydgeorge_store
    #     or input(
    #         "Would you like to remove all records "
    #         "from the LloydGeorgeRecord Bucket (y/N) "
    #     ).lower()
    #     == "y"
    # ):
    #     copy_to_s3(file_names_and_keys, "source_to_copy_from.pdf")

    exit(0)
