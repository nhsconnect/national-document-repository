import os

from models.nhs_document_reference import NHSDocumentReference
from models.staging_metadata import MetadataFile, StagingMetadata
from tests.unit.conftest import MOCK_LG_BUCKET, TEST_OBJECT_KEY

patient_1_file_1 = MetadataFile(
    file_path="/1234567890/1of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
    page_count="",
    gp_practice_code="",
    nhs_number="1234567890",
    section="LG",
    sub_section="",
    scan_date="03/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)
patient_1_file_2 = MetadataFile(
    file_path="/1234567890/2of2_Lloyd_George_Record_[Joe Bloggs]_[1234567890]_[25-12-2019].pdf",
    page_count="",
    gp_practice_code="",
    nhs_number="1234567890",
    section="LG",
    sub_section="",
    scan_date="03/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)

patient_1 = StagingMetadata(
    nhs_number="1234567890", files=[patient_1_file_1, patient_1_file_2]
)

patient_2_file_1 = MetadataFile(
    file_path="1of1_Lloyd_George_Record_[Joe Bloggs_invalid]_[1234567891]_[25-12-2019].txt",
    page_count="",
    nhs_number="1234567891",
    gp_practice_code="",
    section="LG",
    sub_section="",
    scan_date="04/09/2022",
    scan_id="NEC",
    user_id="NEC",
    upload="04/10/2023",
)

patient_2 = StagingMetadata(nhs_number="1234567891", files=[patient_2_file_1])

EXPECTED_PARSED_METADATA = [patient_1, patient_2]


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


def make_valid_lg_file_names(total_number: int, nhs_number: str = "1234567890"):
    return [
        f"{i}of{total_number}_Lloyd_George_Record_[Joe Bloggs]_[{nhs_number}]_[25-12-2019].pdf"
        for i in range(1, total_number + 1)
    ]


def build_test_staging_metadata(file_names: list[str], nhs_number: str = "1234567890"):
    files = []
    for file_name in file_names:
        source_file_path = f"/{nhs_number}/{file_name}"
        files.append(
            patient_1_file_1.model_copy(update={"file_path": source_file_path})
        )
    return StagingMetadata(files=files, nhs_number=nhs_number)


def build_test_sqs_message(staging_metadata: StagingMetadata):
    return {
        "body": staging_metadata.model_dump_json(by_alias=True),
        "eventSource": "aws:sqs",
    }


def build_test_document_reference(file_name: str, nhs_number: str = "1234567890"):
    return NHSDocumentReference(
        nhs_number=nhs_number,
        content_type="application/pdf",
        file_name=file_name,
        reference_id=TEST_OBJECT_KEY,
        s3_bucket_name=MOCK_LG_BUCKET,
    )


TEST_NHS_NUMBER = "1234567890"
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

TEST_SQS_MESSAGE_WITH_INVALID_FILENAME = build_test_sqs_message(TEST_STAGING_METADATA_WITH_INVALID_FILENAME)
TEST_STAGING_METADATA_WITH_INVALID_FILENAME.model_dump_json(by_alias=True)
