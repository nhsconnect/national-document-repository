import argparse
import csv
import os
import shutil
from datetime import date, datetime
from enum import StrEnum
from glob import glob
from io import BytesIO
from typing import Any, Dict, List, NamedTuple

import boto3
from botocore.exceptions import ClientError

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


def build_test_files_for_bulk_upload(
    small_data_file: bool, number_of_files_for_each_patient: int = 3
):
    # Run this test will generate a random test folder at output
    # This can be run without AWS creds
    global NHS_NUMBER_INVALID_FILE_NAME
    global NHS_NUMBER_INVALID_FILES_NUMBER
    global NHS_NUMBER_INVALID_FILE_NHS_NUMBER
    global NHS_NUMBER_MISSING_FILES
    global NHS_NUMBER_NO_FILES
    global NHS_NUMBER_INFECTED
    global NHS_NUMBER_INVALID_PATIENT_NAME
    global NHS_NUMBER_DUPLICATE_IN_METADATA
    global NHS_NUMBER_WITH_DIFFERENT_UPLOADER
    global NHS_NUMBER_ALREADY_UPLOADED
    global NHS_NUMBER_WRONG_DOB
    # select which GP to use from here
    patients = []
    for filename in PatientsDataFile:
        patient_from_csv = get_patients(filename)
        if filename in [PatientsDataFile.H81109, PatientsDataFile.JigginsLane]:
            if small_data_file and filename == PatientsDataFile.H81109:
                patient_from_csv = patient_from_csv[:100]

            one_percent_count = max(1, len(patient_from_csv) // 100)
            NHS_NUMBER_INVALID_FILE_NAME.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[:one_percent_count]
                ]
            )
            NHS_NUMBER_INVALID_FILES_NUMBER.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        one_percent_count : 2 * one_percent_count
                    ]
                ]
            )
            NHS_NUMBER_INVALID_FILE_NHS_NUMBER.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        2 * one_percent_count : 3 * one_percent_count
                    ]
                ]
            )
            NHS_NUMBER_MISSING_FILES.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        3 * one_percent_count : 4 * one_percent_count
                    ]
                ]
            )
            NHS_NUMBER_NO_FILES.extend(
                [
                    f"/{patient.get('NHS_NO')}"
                    for patient in patient_from_csv[
                        4 * one_percent_count : 5 * one_percent_count
                    ]
                ]
            )
            NHS_NUMBER_INFECTED.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        5 * one_percent_count : 6 * one_percent_count
                    ]
                ]
            )
            NHS_NUMBER_INVALID_PATIENT_NAME.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        6 * one_percent_count : 7 * one_percent_count
                    ]
                ]
            )
            NHS_NUMBER_DUPLICATE_IN_METADATA.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        7 * one_percent_count : 8 * one_percent_count
                    ]
                ]
            )

            for patient in patient_from_csv[
                8 * one_percent_count : 9 * one_percent_count
            ]:
                NHS_NUMBER_WITH_DIFFERENT_UPLOADER.append(patient.get("NHS_NO"))

            for patient in patient_from_csv[
                9 * one_percent_count : 10 * one_percent_count
            ]:
                NHS_NUMBER_ALREADY_UPLOADED.append(patient.get("NHS_NO"))

            NHS_NUMBER_WRONG_DOB.extend(
                [
                    patient.get("NHS_NO")
                    for patient in patient_from_csv[
                        10 * one_percent_count : 11 * one_percent_count
                    ]
                ]
            )

        patients.extend(parse_patient_record(record) for record in patient_from_csv)
    create_previous_uploads()

    all_file_paths = build_file_paths_for_all_patients(
        patient_list=patients, total_number_for_each=number_of_files_for_each_patient
    )

    metadata_content = build_metadata_csv(
        patient_list=patients, total_number_for_each=number_of_files_for_each_patient
    )
    prepare_test_directory(all_file_paths, metadata_content)
    create_scenario_report()


def get_patients(filename: str) -> List[Dict]:
    patients = []
    with open(f"../test_patients_data/{filename}", mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            patients.append(row)  # Append each row (as a dictionary) to the list
    return patients


def parse_patient_record(raw_record: dict) -> Patient:
    nhs_number = raw_record["NHS_NO"]
    name_parts = [
        raw_record["GIVEN_NAME"],
        raw_record["OTHER_GIVEN_NAME"],
        raw_record["FAMILY_NAME"],
    ]
    if nhs_number in NHS_NUMBER_INVALID_PATIENT_NAME:
        name_parts = [s + "abc" for s in name_parts]
    full_name = " ".join(name_part for name_part in name_parts if name_part)
    date_of_birth = raw_record["DOB"].replace("/", "-")
    if nhs_number in NHS_NUMBER_WRONG_DOB:
        date_of_birth = "12/01/1223"
    ods_code = raw_record["GPP"]
    if nhs_number in NHS_NUMBER_WITH_DIFFERENT_UPLOADER:
        ods_code = "AB12XX"
    return Patient(full_name, date_of_birth, nhs_number, ods_code)


def flatten(input_list: List[List[Any]]) -> List[Any]:
    return [elem for sublist in input_list for elem in sublist]


def build_valid_lg_file_name(
    patient: Patient, file_count: int = 1, total_number: int = 3
) -> str:
    return (
        f"{file_count}of{total_number}_Lloyd_George_Record_["
        f"{patient.full_name}]_[{patient.nhs_number}]_[{patient.date_of_birth}].pdf"
    )


def build_invalid_lg_file_name(
    patient: Patient, file_count: int = 1, total_number: int = 3
) -> str:
    return (
        f"{file_count}of{total_number}_Lloyd_George_Record_["
        f"{patient.nhs_number}]_[{patient.full_name}]_[{patient.date_of_birth}].pdf"
    )


def build_invalid_file_number_lg_file_name(
    patient: Patient, file_count: int = 1, total_number: int = 3
) -> str:
    return (
        f"{file_count}of{total_number - 1}_Lloyd_George_Record["
        f"{patient.full_name}]_[{patient.nhs_number}]_[{patient.date_of_birth}].pdf"
    )


def build_invalid_nhs_number_lg_file_name(
    patient: Patient, file_count: int = 1, total_number: int = 3
) -> str:
    return (
        f"{file_count}of{total_number}_Lloyd_George_Record_["
        f"{patient.full_name}]_[{str(patient.nhs_number)[:-2]}01]_[{patient.date_of_birth}].pdf"
    )


def build_many_file_names(patient: Patient, total_number: int = 3) -> List[str]:
    return [
        build_valid_lg_file_name(patient, file_count, total_number)
        for file_count in range(1, total_number + 1)
    ]


def build_many_file_paths(patient: Patient, total_number: int = 3) -> List[str]:
    build_function = return_build_function_by_nhs_number(str(patient.nhs_number))
    if str(patient.nhs_number) in NHS_NUMBER_MISSING_FILES:
        return [
            build_file_path(
                patient, build_valid_lg_file_name(patient, file_count, total_number)
            )
            for file_count in range(1, total_number)
        ]
    return [
        build_file_path(patient, build_function(patient, file_count, total_number))
        for file_count in range(1, total_number + 1)
    ]


def return_build_function_by_nhs_number(nhs_number: str):
    if nhs_number in NHS_NUMBER_INVALID_FILE_NAME:
        return build_invalid_lg_file_name
    elif nhs_number in NHS_NUMBER_INVALID_FILES_NUMBER:
        return build_invalid_file_number_lg_file_name
    elif nhs_number in NHS_NUMBER_INVALID_FILE_NHS_NUMBER:
        return build_invalid_nhs_number_lg_file_name
    return build_valid_lg_file_name


def build_file_path(patient: Patient, file_name: str) -> str:
    return f"/{patient.nhs_number}/{file_name}"


def build_file_paths_for_all_patients(
    patient_list: List[Patient], total_number_for_each: int = 3
) -> List[str]:
    return flatten(
        [
            build_many_file_paths(patient, total_number=total_number_for_each)
            for patient in patient_list
        ]
    )


def build_metadata_csv_rows(patient: Patient, total_number: int = 3) -> list[str]:
    date_today = date.today().strftime("%d/%m/%Y")
    section = "LG"
    sub_section = ""
    scan_date = "01/01/2023"
    scan_id = "NEC"
    user_id = "NEC"
    upload_date = date_today

    rows = []

    file_range = range(1, total_number + 1)
    if str(patient.nhs_number) in NHS_NUMBER_MISSING_FILES:
        file_range = file_range[:-1]
    for file_count in file_range:
        build_function = return_build_function_by_nhs_number(str(patient.nhs_number))
        file_name = build_function(patient, file_count, total_number)
        file_path = build_file_path(patient, file_name)

        row = ",".join(
            [
                file_path,
                str(file_count),
                patient.ods_code,
                str(patient.nhs_number),
                section,
                sub_section,
                scan_date,
                scan_id,
                user_id,
                upload_date,
            ]
        )
        rows.append(row)

    return rows


def build_metadata_csv(
    patient_list: List[Patient], total_number_for_each: int = 3
) -> str:
    header_row = (
        "FILEPATH,PAGE COUNT,GP-PRACTICE-CODE,NHS-NO,"
        "SECTION,SUB-SECTION,SCAN-DATE,SCAN-ID,USER-ID,UPLOAD"
    )
    all_rows = []
    for patient in patient_list:
        row = build_metadata_csv_rows(
            patient=patient, total_number=total_number_for_each
        )
        all_rows.append(row)
        if patient.nhs_number in NHS_NUMBER_DUPLICATE_IN_METADATA:
            all_rows.append(row)

    flatten_rows = [row for sublist in all_rows for row in sublist]
    return "\n".join([header_row, *flatten_rows])


def create_scenario_report():
    with open("scenario_report.txt", "w") as f:
        f.write("nhs numbers with invalid file name: ")
        f.write(", ".join(NHS_NUMBER_INVALID_FILE_NAME) + "\n")
        f.write("nhs numbers with invalid number of files: ")
        f.write(", ".join(NHS_NUMBER_INVALID_FILES_NUMBER) + "\n")
        f.write("nhs numbers with invalid nhs number: ")
        f.write(", ".join(NHS_NUMBER_INVALID_FILE_NHS_NUMBER) + "\n")
        f.write("nhs numbers with missing files: ")
        f.write(", ".join(NHS_NUMBER_MISSING_FILES) + "\n")
        f.write("nhs numbers with invalid patient name: ")
        f.write(", ".join(NHS_NUMBER_INVALID_PATIENT_NAME) + "\n")
        f.write("nhs numbers with no files: ")
        f.write(", ".join(NHS_NUMBER_NO_FILES) + "\n")
        f.write("nhs numbers with duplication in metadata: ")
        f.write(", ".join(NHS_NUMBER_DUPLICATE_IN_METADATA) + "\n")
        f.write("nhs numbers with a different uploader ods code from patient: ")
        f.write(", ".join(NHS_NUMBER_WITH_DIFFERENT_UPLOADER) + "\n")
        f.write("nhs numbers already in the repo: ")
        f.write(", ".join(NHS_NUMBER_ALREADY_UPLOADED) + "\n")
        f.write("nhs numbers with wrong date of birth: ")
        f.write(", ".join(NHS_NUMBER_WRONG_DOB) + "\n")
        f.write("nhs numbers with infected files: ")
        f.write(", ".join(NHS_NUMBER_INFECTED) + "\n")


def prepare_test_directory(file_path_list: List[str], metadata_file_content: str):
    output_folder = "../output"
    source_pdf_file = "../source_to_copy_from.pdf"

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.mkdir(output_folder)
    output_folder_path = os.path.abspath(os.path.join(os.getcwd(), output_folder))

    metadata_file_path = os.path.join(output_folder_path, "metadata.csv")
    with open(metadata_file_path, "w") as f:
        f.write(metadata_file_content)

    for file_path in file_path_list:
        if file_path.startswith(tuple(NHS_NUMBER_NO_FILES)):
            continue
        output_path = os.path.join(output_folder_path, file_path.lstrip("/"))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copyfile(source_pdf_file, output_path)


def upload_lg_files_to_staging():
    # this one is a bit flaky
    os.chdir("../")

    files = ["metadata.csv"] + glob("*/*Lloyd_George_Record*.pdf")
    client = boto3.client("s3")
    for file in files:
        client.upload_file(
            Filename=file,
            Bucket=STAGING_BUCKET,
            Key=file,
            ExtraArgs={"StorageClass": "INTELLIGENT_TIERING"},
        )

        scan_result = "Clean"
        if file.startswith(tuple(NHS_NUMBER_INFECTED)):
            scan_result = "Infected"
        client.put_object_tagging(
            Bucket=STAGING_BUCKET,
            Key=file,
            Tagging={
                "TagSet": [
                    {"Key": "scan-result", "Value": scan_result},
                    {"Key": "date-scanned", "Value": "2023-11-14T21:10:33Z"},
                ]
            },
        )


def prepare_and_upload_test_files(
    file_tuples: list[tuple[str, str]],  # (s3_key, nhs_number)
    metadata_file_content: str,
    fake_pdf_content: bytes = b"%PDF-1.4\n%Fake PDF content",
    scan_date: str = None,
):
    """
    Generates fake files and uploads them to S3 without writing anything locally.

    Args:
        file_tuples: List of (s3_key, nhs_number).
        metadata_file_content: Content to upload as metadata.csv.
        fake_pdf_content: Binary content of a fake PDF.
        scan_date: ISO 8601 scan timestamp.
    """
    if scan_date is None:
        scan_date = datetime.utcnow().isoformat()

    s3 = boto3.client("s3")

    # Upload metadata file
    s3.put_object(
        Bucket=STAGING_BUCKET,
        Key="metadata.csv",
        Body=metadata_file_content,
        ContentType="text/csv",
        StorageClass="INTELLIGENT_TIERING",
    )

    # Upload each test file and tag it
    for s3_key, nhs_number in file_tuples:
        # Upload fake PDF
        s3.upload_fileobj(
            Fileobj=BytesIO(fake_pdf_content),
            Bucket=STAGING_BUCKET,
            Key=s3_key,
            ExtraArgs={
                "ContentType": "application/pdf",
                "StorageClass": "INTELLIGENT_TIERING",
            },
        )

        # Determine scan result based on NHS number
        scan_result = (
            "Infected" if nhs_number.startswith(tuple(NHS_NUMBER_INFECTED)) else "Clean"
        )

        # Add scan-result tags
        s3.put_object_tagging(
            Bucket=STAGING_BUCKET,
            Key=s3_key,
            Tagging={
                "TagSet": [
                    {"Key": "scan-result", "Value": scan_result},
                    {"Key": "date-scanned", "Value": scan_date},
                ]
            },
        )


def removing_previous_uploads():
    dynamodb = boto3.resource("dynamodb")

    bulk_table = dynamodb.Table(BULK_UPLOAD_TABLE_NAME)
    scan_and_remove_items(bulk_table)

    bulk_table = dynamodb.Table(LG_TABLE_NAME)
    scan_and_remove_items(bulk_table)


def create_previous_uploads():
    dynamodb = boto3.resource("dynamodb")

    bulk_table = dynamodb.Table(LG_TABLE_NAME)
    items = []
    for nhs_number in NHS_NUMBER_ALREADY_UPLOADED:
        items.append(
            {
                "ID": f"dfss-{nhs_number}-sdsds",
                "Created": "2022-04-26T14:43:18.142567Z",
                "FileLocation": f"s3://lloyd-george-store/{nhs_number}/111111111111111111111",
                "FileName": f"1of1_Lloyd_George_Record_[{nhs_number}]_[]_[].pdf",
                "NhsNumber": nhs_number,
                "Uploaded": True,
                "Uploading": False,
                "VirusScannerResult": "Clean",
                "ContentType": "application/pdf",
                "CurrentGpOds": "ABC123",
                "LastUpdated": 1727355081,
                "TTL": 1732530786,
            }
        )
    create_items(bulk_table, items)


def scan_and_remove_items(table):
    # Scan the table to get all items
    response = table.scan()
    items = response["Items"]

    with table.batch_writer() as batch:
        # Loop through the items and delete each one
        for item in items:
            batch.delete_item(Key={"ID": item["ID"]})

        # Handle pagination if there are more items
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items = response["Items"]
            for item in items:
                batch.delete_item(Key={"ID": item["ID"]})
    print("All items deleted.")


def create_items(table, items):
    try:
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
    except ClientError as e:
        print(f"Error writing items: {e.response['Error']['Message']}")
        exit(1)


def check_confirmation(confirmation: str):
    if confirmation in ["Y", "y", "Yes", "YES"]:
        return True
    return False


def clear_lg_store():
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(LLOYD_GEORGE_BUCKET)

    bucket.objects.all().delete()

    bucket.object_versions.delete()


def download_all_files_from_s3(bucket_name, download_path):
    s3 = boto3.client("s3")
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            for obj in response["Contents"]:
                file_key = obj["Key"]
                local_file_path = f"{download_path}/{file_key}"
                s3.download_file(bucket_name, file_key, local_file_path)
                print(f"File {file_key} downloaded successfully to {local_file_path}.")
        else:
            print("No files found in the bucket.")
    except Exception as e:
        print(f"Error downloading files: {str(e)}")


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
    parser.add_argument(
        "--data-file",
        help="Data file to build against: 1 for Combi 8000, 2 for Combi 300.",
    )
    parser.add_argument(
        "--num-files", type=int, default=1, help="Number of files per patient to build."
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

    if (
        args.delete_table
        or input(
            "Would you like to remove all existing data from the dynamo tables? (y/N) "
        ).lower()
        == "y"
    ):
        removing_previous_uploads()

    if (
        args.download_data
        or input("Would you like to download the test data from S3? (y/N) ").lower()
        == "y"
    ):
        download_all_files_from_s3("ndr-testdata", "../test_patients_data")

    if (
        args.build_files
        or input("Would you like to build the test files? (y/N) ").lower() == "y"
    ):
        is_small_data_file = (
            args.data_file != "combi8000"
            or input("Input combi8000 or combi300:") != "combi8000"
        )
        file_number = args.num_files or int(
            input("How many files per patient do you wish to generate: ")
        )
        build_test_files_for_bulk_upload(is_small_data_file, file_number)

    if (
        args.upload
        or input(
            "Would you like to upload the test files to S3 "
            "and add the virus-scan tag? (y/N) "
        ).lower()
        == "y"
    ):
        upload_lg_files_to_staging()
    if (
        args.empty_lloydgeorge_store
        or input(
            "Would you like to remove all records "
            "from the LloydGeorgeRecord Bucket (y/N) "
        ).lower()
        == "y"
    ):
        clear_lg_store()

    exit(0)
