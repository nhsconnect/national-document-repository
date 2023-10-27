import json

from models.staging_metadata import StagingMetadata
from tests.unit.helpers.data.bulk_upload.test_data import (
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567890,
    EXPECTED_SQS_MSG_FOR_PATIENT_1234567891, patient_1, patient_2)


def test_serialise_staging_data_to_json():
    assert (
        patient_1.model_dump_json(by_alias=True)
        == EXPECTED_SQS_MSG_FOR_PATIENT_1234567890
    )
    assert (
        patient_2.model_dump_json(by_alias=True)
        == EXPECTED_SQS_MSG_FOR_PATIENT_1234567891
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
            json.loads(EXPECTED_SQS_MSG_FOR_PATIENT_1234567891)
        )
        == patient_2
    )
