import json

from models.staging_metadata import StagingMetadata
from tests.unit.helpers.data.bulk_upload.test_data import (
    EXPECTED_SQS_MSG_FOR_PATIENT_123456789,
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
    patient_1,
    patient_2,
)


def test_serialise_staging_data_to_json():
    assert (
        patient_1.model_dump_json(by_alias=True)
        == EXPECTED_SQS_MSG_FOR_PATIENT_1234567890
    )
    assert (
        patient_2.model_dump_json(by_alias=True)
        == EXPECTED_SQS_MSG_FOR_PATIENT_123456789
    )


def test_deserialise_json_to_staging_data():
    assert (
        StagingMetadata.model_validate(
            json.loads(EXPECTED_SQS_MSG_FOR_PATIENT_1234567890)
        )
        == patient_1
    )
    assert (
        StagingMetadata.model_validate(
            json.loads(EXPECTED_SQS_MSG_FOR_PATIENT_123456789)
        )
        == patient_2
    )


def test_staging_metadata_with_field_corrections():
    input_dict = {
        "NHS-NO": "1000000000",
        "files": [
            {
                "FILEPATH": "/abc/xyz/01of01_Lloyd_George_Record.pdf",
                "PAGE COUNT": "10",
                "GP-PRACTICE-CODE": "A12345",
                "SECTION": "General",
                "SUB-SECTION": None,
                "SCAN-DATE": "01/01/2023",
                "SCAN-ID": "scan001",
                "USER-ID": "user001",
                "UPLOAD": "yes",
            }
        ],
        "corrections": {
            "/abc/xyz/01of01_Lloyd_George_Record.pdf": "/abc/xyz/1of1_Lloyd_George_Record.pdf"
        },
    }

    # Deserialize
    metadata_obj = StagingMetadata.model_validate(input_dict)
    assert metadata_obj.nhs_number == "1000000000"
    assert metadata_obj.corrections == {
        "/abc/xyz/01of01_Lloyd_George_Record.pdf": "/abc/xyz/1of1_Lloyd_George_Record.pdf"
    }

    # Serialize
    json_output = metadata_obj.model_dump_json(by_alias=True)
    parsed_back = json.loads(json_output)

    assert parsed_back["corrections"] == input_dict["corrections"]
    assert parsed_back["NHS-NO"] == "1000000000"
    assert (
        parsed_back["files"][0]["FILEPATH"] == "/abc/xyz/01of01_Lloyd_George_Record.pdf"
    )
