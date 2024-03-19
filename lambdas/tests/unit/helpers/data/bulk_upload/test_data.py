import os

from enums.virus_scan_result import VirusScanResult
from freezegun import freeze_time
from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import MetadataFile, StagingMetadata
from tests.unit.conftest import MOCK_LG_BUCKET, TEST_CURRENT_GP_ODS, TEST_OBJECT_KEY

sample_metadata_model = MetadataFile(
    file_path="/1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
    page_count="",
    gp_practice_code="Y12345",
    section="LG",
    sub_section="",
    scan_date="03/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)
patient_1_file_1 = sample_metadata_model.model_copy()
patient_1_file_2 = sample_metadata_model.model_copy(
    update={
        "file_path": "/1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf"
    }
)
patient_1 = StagingMetadata(
    nhs_number="1234567890", files=[patient_1_file_1, patient_1_file_2], retries=0
)

patient_2_file_1 = sample_metadata_model.model_copy(
    update={
        "file_path": "1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[1234567891]_[25-12-2019].txt",
        "scan_date": "04/09/2022",
    }
)
patient_2 = StagingMetadata(
    nhs_number="1234567891", files=[patient_2_file_1], retries=0
)
MOCK_METADATA = [patient_1, patient_2]


patient_1_file_1_with_temp_nhs_number = patient_1_file_1.model_copy(
    update={"nhs_number": "1234567890"}
)
patient_1_file_2_with_temp_nhs_number = patient_1_file_2.model_copy(
    update={"nhs_number": "1234567890"}
)
patient_2_file_1_with_temp_nhs_number = patient_2_file_1.model_copy(
    update={"nhs_number": "1234567891"}
)
patient_1_with_temp_nhs_number = StagingMetadata(
    nhs_number="1234567890",
    files=[
        patient_1_file_1_with_temp_nhs_number,
        patient_1_file_2_with_temp_nhs_number,
    ],
)
patient_2_with_temp_nhs_number = StagingMetadata(
    nhs_number="1234567891", files=[patient_2_file_1_with_temp_nhs_number]
)
EXPECTED_PARSED_METADATA = [
    patient_1_with_temp_nhs_number,
    patient_2_with_temp_nhs_number,
]


def readfile(filename: str) -> str:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r") as file:
        file_content = file.read()
    return file_content


EXPECTED_SQS_MSG_FOR_PATIENT_1234567890 = readfile(
    "expect_sqs_msg_for_patient_1234567890.json"
)
EXPECTED_SQS_MSG_FOR_PATIENT_1234567891 = readfile(
    "expect_sqs_msg_for_patient_1234567891.json"
)


def make_valid_lg_file_names(
    total_number: int, nhs_number: str = "9000000009", patient_name: str = "Jane Smith"
):
    return [
        f"{i}of{total_number}_Lloyd_George_Record_[{patient_name}]_[{nhs_number}]_[22-10-2010].pdf"
        for i in range(1, total_number + 1)
    ]


def make_s3_file_paths(file_names: list[str], nhs_number: str = "9000000009"):
    return [f"{nhs_number}/{file_name}" for file_name in file_names]


def build_test_staging_metadata_from_patient_name(
    patient_name: str, nhs_number: str = "9000000009"
) -> StagingMetadata:
    file_names = make_valid_lg_file_names(
        total_number=3, nhs_number=nhs_number, patient_name=patient_name
    )
    return build_test_staging_metadata(file_names=file_names, nhs_number=nhs_number)


def build_test_staging_metadata(file_names: list[str], nhs_number: str = "9000000009"):
    files = []
    for file_name in file_names:
        source_file_path = f"/{nhs_number}/{file_name}"
        files.append(
            sample_metadata_model.model_copy(update={"file_path": source_file_path})
        )
    return StagingMetadata(files=files, nhs_number=nhs_number)


def build_test_sqs_message(staging_metadata: StagingMetadata):
    return {
        "body": staging_metadata.model_dump_json(by_alias=True),
        "eventSource": "aws:sqs",
        "messageAttributes": {
            "NhsNumber": {"stringValue": staging_metadata.nhs_number}
        },
    }


def build_test_sqs_message_from_nhs_number(nhs_number: str) -> dict:
    file_names = make_valid_lg_file_names(total_number=3, nhs_number=nhs_number)
    staging_metadata = build_test_staging_metadata(
        file_names=file_names, nhs_number=nhs_number
    )
    return build_test_sqs_message(staging_metadata)


@freeze_time("2024-01-01 12:00:00")
def build_test_document_reference(file_name: str, nhs_number: str = "9000000009"):
    doc_ref = NHSDocumentReference(
        nhs_number=nhs_number,
        content_type="application/pdf",
        file_name=file_name,
        reference_id=TEST_OBJECT_KEY,
        s3_bucket_name=MOCK_LG_BUCKET,
        current_gp_ods=TEST_CURRENT_GP_ODS,
    )
    doc_ref.virus_scanner_result = VirusScanResult.CLEAN
    return doc_ref


TEST_NHS_NUMBER_FOR_BULK_UPLOAD = "9000000009"
TEST_STAGING_METADATA = build_test_staging_metadata(make_valid_lg_file_names(3))
TEST_SQS_MESSAGE = build_test_sqs_message(TEST_STAGING_METADATA)
TEST_FILE_METADATA = TEST_STAGING_METADATA.files[0]

TEST_STAGING_METADATA_WITH_INVALID_FILENAME = build_test_staging_metadata(
    [*make_valid_lg_file_names(2), "invalid_file_name.txt"]
)

TEST_DOCUMENT_REFERENCE = build_test_document_reference(make_valid_lg_file_names(3)[0])
TEST_DOCUMENT_REFERENCE_LIST = [
    build_test_document_reference(file_name)
    for file_name in make_valid_lg_file_names(3)
]

TEST_SQS_MESSAGE_WITH_INVALID_FILENAME = build_test_sqs_message(
    TEST_STAGING_METADATA_WITH_INVALID_FILENAME
)
TEST_STAGING_METADATA_WITH_INVALID_FILENAME.model_dump_json(by_alias=True)

TEST_EVENT_WITH_ONE_SQS_MESSAGE = {"Records": [TEST_SQS_MESSAGE]}

TEST_SQS_MESSAGES_AS_LIST = [
    TEST_SQS_MESSAGE,
    TEST_SQS_MESSAGE_WITH_INVALID_FILENAME,
    TEST_SQS_MESSAGE,
]

TEST_EVENT_WITH_NO_SQS_MESSAGES = {"Records": []}

TEST_EVENT_WITH_SQS_MESSAGES = {"Records": TEST_SQS_MESSAGES_AS_LIST}

TEST_SQS_10_MESSAGES_AS_LIST = [
    build_test_sqs_message_from_nhs_number(str(nhs_number))
    for nhs_number in range(9_000_000_000, 9_000_000_010)
]

TEST_EVENT_WITH_10_SQS_MESSAGES = {"Records": TEST_SQS_10_MESSAGES_AS_LIST}
