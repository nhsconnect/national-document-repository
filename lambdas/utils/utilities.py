import os
import re
import uuid
from urllib.parse import urlparse

from inflection import camelize
from services.mock_pds_service import MockPdsApiService
from services.pds_api_service import PdsApiService
from utils.exceptions import InvalidResourceIdException


def validate_nhs_number(patient_id: str) -> bool:
    pattern = re.compile("^\\d{10}$")

    if not bool(pattern.match(patient_id)):
        raise InvalidResourceIdException("Invalid NHS number")

    return True


def camelize_dict(data: dict) -> dict:
    """
    Reformat a dictionary so it's keys are returned as camelcase suitable for JSON response
        :param data: dict to reformat

    example usage:
        values = {"FileName": "test", "VirusScannerResult": "test"}
        result = camelize_dict(values)

    result:
        {"fileName": "test", "virusScannerResult": "test"}
    """
    camelized_data = {}
    for key, value in data.items():
        camelized_data[camelize(key, uppercase_first_letter=False)] = value
    return camelized_data


def create_reference_id() -> str:
    return str(uuid.uuid4())


def get_pds_service():
    return (
        PdsApiService
        if (os.getenv("PDS_FHIR_IS_STUBBED") == "false")
        else MockPdsApiService
    )


def redact_id_to_last_4_chars(str_id: str) -> str:
    return str_id[-4:]


def get_file_key_from_s3_url(s3_url: str) -> str:
    return urlparse(s3_url).path.lstrip("/")
