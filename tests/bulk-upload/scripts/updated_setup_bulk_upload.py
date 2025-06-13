import argparse
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import boto3

SOURCE_PDF_FILE_NAME = "source_to_copy_from.pdf"
SOURCE_PDF_FILE = "../source_to_copy_from.pdf"
UPDATED_SOURCE_PDF_FILE = "../updated_source_to_copy_from.pdf"
NHS_NUMBER = "1000000000"

CSV_HEADER_ROW = (
    "FILEPATH,PAGE COUNT,GP-PRACTICE-CODE,NHS-NO,"
    "SECTION,SUB-SECTION,SCAN-DATE,SCAN-ID,USER-ID,UPLOAD"
)
S3_STORAGE_CLASS = "INTELLIGENT_TIERING"

S3_SCAN_TAGS = [
    {"Key": "scan-result", "Value": "Clean"},
    {"Key": "date-scanned", "Value": "2023-11-14T21:10:33Z"},
]
client = boto3.client("s3")

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


def generate_file_name(
    current_file_number: int, number_of_files: int, person_name: str, nhs_number: str
) -> str:
    return (
        f"{current_file_number}of{number_of_files}"
        f"_Lloyd_George_Record_[{person_name}]"
        f"_[{nhs_number}]_[22-10-2010].pdf"
    )


def build_file_path(nhs_number: str, file_name: str) -> str:
    return f"{nhs_number}/{file_name}"


def create_test_file_keys_and_metadata_rows(
    requested_patients_number: int = 2, number_of_files_for_each_patient: int = 3
):
    result = []
    nhs_number = NHS_NUMBER
    metadata_rows = []

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

            metadata_rows.append(
                build_metadata_csv_row(
                    file_key, file_count=file_num, nhs_number=nhs_number
                )
            )
            result.append(file_key)
    metadata_content = "\n".join([CSV_HEADER_ROW, *metadata_rows])
    return result, metadata_content


# def copy_to_s3(file_names_and_keys: list[tuple[str, str]], source_file_key: str):
#     for file_name, file_key in file_names_and_keys:
#         client.copy_object(
#             Bucket=STAGING_BUCKET,
#             Key=file_key,
#             CopySource={"Bucket": STAGING_BUCKET, "Key": source_file_key},
#             StorageClass=S3_STORAGE_CLASS,
#         )


def inflate_pdf_file(source_pdf_path: str, target_pdf_path: str, target_size_mb: float):
    with open(source_pdf_path, "rb") as original:
        content = original.read()

    with open(target_pdf_path, "wb") as new_pdf:
        new_pdf.write(content)

        current_size = len(content)
        target_size = int(target_size_mb * 1024 * 1024)
        padding_size = target_size - current_size

        if padding_size > 0:
            # Append a PDF comment block that does nothing but take up space
            padding = b"\n%" + b"0" * max(padding_size - 2, 0)
            new_pdf.write(padding)


def upload_source_file_to_staging(source_pdf_path: str, file_key: str):
    with open(source_pdf_path, "rb") as buffer:
        client.put_object(
            Bucket=STAGING_BUCKET,
            Key=file_key,
            Body=buffer,
            StorageClass=S3_STORAGE_CLASS,
        )

        client.put_object_tagging(
            Bucket=STAGING_BUCKET,
            Key=file_key,
            Tagging={"TagSet": S3_SCAN_TAGS},
        )


def delete_file_from_staging(file_key: str):
    client.delete_object(Bucket=STAGING_BUCKET, Key=file_key)


def upload_lg_files_to_staging(lg_file_keys: list[str], source_pdf_file_key):
    def copy_and_tag(target_file_key):
        client.copy_object(
            CopySource={"Bucket": STAGING_BUCKET, "Key": source_pdf_file_key},
            Bucket=STAGING_BUCKET,
            Key=target_file_key,
            StorageClass=S3_STORAGE_CLASS,
            MetadataDirective="COPY",
        )
        client.put_object_tagging(
            Bucket=STAGING_BUCKET,
            Key=target_file_key,
            Tagging={"TagSet": S3_SCAN_TAGS},
        )
        return target_file_key

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(copy_and_tag, key) for key in lg_file_keys]
        for future in as_completed(futures):
            try:
                key = future.result()
                print(f"Finished processing {key}")
            except Exception as e:
                print(f"Failed processing {key}: {e}")


def check_confirmation(confirmation: str) -> bool:
    return confirmation.strip().lower() in {"y", "yes"}


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
        "--file-size",
        type=float,
        help="Target file size in MB",
    )
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


def build_metadata_csv_row(file_key: str, file_count: int, nhs_number: str) -> str:
    date_today = date.today().strftime("%d/%m/%Y")
    section = "LG"
    sub_section = ""
    scan_date = "01/01/2023"
    scan_id = "NEC"
    user_id = "NEC"
    upload_date = date_today
    file_path = file_key
    row = ",".join(
        [
            file_path,
            str(file_count),
            "M85143",
            nhs_number,
            section,
            sub_section,
            scan_date,
            scan_id,
            user_id,
            upload_date,
        ]
    )
    return row


def upload_metadata_to_s3(body: str):
    client.put_object(
        Bucket=STAGING_BUCKET,
        Key="metadata.csv",
        Body=body,
        ContentType="text/csv",
        StorageClass=S3_STORAGE_CLASS,
    )


if __name__ == "__main__":
    args = get_user_input()
    print("Welcome to test set up script")
    ENVIRONMENT = args.environment or input(
        "Please enter the environment you want to use:"
    )
    STAGING_BUCKET = f"{ENVIRONMENT}-staging-bulk-store"

    if not args.environment:
        env_confirmation = input(
            f"Please confirm you want to use {ENVIRONMENT} (y/N): "
        )
        if not check_confirmation(env_confirmation):
            print("Exiting Script")
            exit(0)

    number_of_patients = args.num_patients or int(
        input("How many patients do you wish to generate")
    )
    file_number = args.num_files or int(
        input("How many files per patient do you wish to generate: ")
    )
    file_size = args.file_size or float(
        input("What is the file size in MB you wish to generate: ")
    )
    file_keys, metadata_content = create_test_file_keys_and_metadata_rows(
        int(number_of_patients), int(file_number)
    )

    if (
        args.upload
        or input(
            "Would you like to upload the test files to S3 "
            "and add the virus-scan tag? (y/N) "
        ).lower()
        == "y"
    ):

        upload_metadata_to_s3(body=metadata_content)

        inflate_pdf_file(
            SOURCE_PDF_FILE, UPDATED_SOURCE_PDF_FILE, target_size_mb=file_size
        )
        upload_source_file_to_staging(UPDATED_SOURCE_PDF_FILE, SOURCE_PDF_FILE_NAME)

        upload_lg_files_to_staging(file_keys, SOURCE_PDF_FILE_NAME)

        delete_file_from_staging(SOURCE_PDF_FILE_NAME)

    exit(0)
