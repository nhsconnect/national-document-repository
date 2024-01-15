import datetime
import os
import re

from botocore.exceptions import ClientError
from enums.pds_ssm_parameters import SSMParameter
from enums.supported_document_types import SupportedDocumentTypes
from models.nhs_document_reference import NHSDocumentReference
from models.pds_models import Patient, PatientDetails
from pydantic import ValidationError
from requests import HTTPError
from services.base.ssm_service import SSMService
from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    PatientRecordAlreadyExistException,
    PdsTooManyRequestsException,
)
from utils.unicode_utils import REGEX_PATIENT_NAME_PATTERN, names_are_matching
from utils.utilities import get_pds_service

logger = LoggingService(__name__)


class LGInvalidFilesException(Exception):
    pass


file_name_invalid = "One or more of the files do not match naming convention"
file_type_invalid = "One or more of the files do not match the required file type"


def validate_lg_file_type(file_type: str):
    if file_type != "application/pdf":
        raise LGInvalidFilesException(file_type_invalid)


def validate_file_name(name: str):
    nhs_number_pattern = "[0-9]{10}"
    lg_regex = rf"[0-9]+of[0-9]+_Lloyd_George_Record_\[{REGEX_PATIENT_NAME_PATTERN}\]_\[{nhs_number_pattern}\]_\[\d\d-\d\d-\d\d\d\d].pdf"
    if not re.fullmatch(lg_regex, name):
        raise LGInvalidFilesException(file_name_invalid)


def check_for_duplicate_files(file_list: list[str]):
    if len(file_list) > len(set(file_list)):
        raise LGInvalidFilesException("One or more of the files has the same filename")


def check_for_number_of_files_match_expected(file_name: str, total_files_number: int):
    lg_number_regex = "of[0-9]+"
    regex_match_result = re.search(lg_number_regex, file_name)
    try:
        expected_number_of_files = int(regex_match_result.group()[2:])
        if total_files_number < expected_number_of_files:
            raise LGInvalidFilesException("There are missing file(s) in the request")
        elif total_files_number > expected_number_of_files:
            raise LGInvalidFilesException(
                "There are more files than the total number in file name"
            )
    except (AttributeError, IndexError, ValueError):
        raise LGInvalidFilesException(file_name_invalid)


def check_for_patient_already_exist_in_repo(nhs_number: str):
    document_service = DocumentService()
    documents_found = document_service.fetch_available_document_references_by_type(
        nhs_number=nhs_number, doc_type=SupportedDocumentTypes.LG
    )

    if documents_found:
        raise PatientRecordAlreadyExistException(
            "Lloyd George already exists for patient, upload cancelled."
        )


def validate_lg_files(file_list: list[NHSDocumentReference]):
    files_name_list = []
    for doc in file_list:
        check_for_number_of_files_match_expected(doc.file_name, len(file_list))
        validate_lg_file_type(doc.content_type)
        validate_file_name(doc.file_name)
        files_name_list.append(doc.file_name)
    check_for_duplicate_files(files_name_list)


def validate_lg_file_names(file_name_list: list[str], nhs_number: str):
    check_for_patient_already_exist_in_repo(nhs_number)

    for file_name in file_name_list:
        check_for_number_of_files_match_expected(file_name, len(file_name_list))
        validate_file_name(file_name)
        file_name_info = extract_info_from_filename(file_name)
        if file_name_info["nhs_number"] != nhs_number:
            raise LGInvalidFilesException(
                "NHS number in file names does not match the given NHS number"
            )
    check_for_duplicate_files(file_name_list)
    check_for_file_names_agrees_with_each_other(file_name_list)


def extract_info_from_filename(filename: str) -> dict:
    page_number = r"(?P<page_no>[1-9][0-9]*)"
    total_page_number = r"(?P<total_page_no>[1-9][0-9]*)"
    patient_name = rf"(?P<patient_name>{REGEX_PATIENT_NAME_PATTERN})"
    nhs_number = r"(?P<nhs_number>\d{10})"
    date_of_birth = r"(?P<date_of_birth>\d\d-\d\d-\d\d\d\d)"

    # ruff: noqa: E501
    lg_regex = rf"{page_number}of{total_page_number}_Lloyd_George_Record_\[{patient_name}\]_\[{nhs_number}\]_\[{date_of_birth}\].pdf"

    if match := re.fullmatch(lg_regex, filename):
        return match.groupdict()
    else:
        raise LGInvalidFilesException(file_name_invalid)


def check_for_file_names_agrees_with_each_other(file_name_list: list[str]):
    expected_common_part = [
        file_name[file_name.index("of") :] for file_name in file_name_list
    ]
    if len(set(expected_common_part)) != 1:
        raise LGInvalidFilesException("File names does not match with each other")


def validate_with_pds_service(
    file_name_list: list[str], patient_details: PatientDetails
):
    try:
        file_name_info = extract_info_from_filename(file_name_list[0])
        patient_name = file_name_info["patient_name"]
        date_of_birth = file_name_info["date_of_birth"]

        date_of_birth = datetime.datetime.strptime(date_of_birth, "%d-%m-%Y").date()
        if patient_details.birth_date != date_of_birth:
            raise LGInvalidFilesException("Patient DoB does not match our records")
        patient_full_name = (
            " ".join([name for name in patient_details.given_Name])
            + " "
            + patient_details.family_name
        )
        logger.info("Verifying patient name against the record in PDS...")

        if not names_are_matching(patient_name, patient_full_name):
            raise LGInvalidFilesException("Patient name does not match our records")

        current_user_ods = get_user_ods_code()
        if patient_details.general_practice_ods != current_user_ods:
            raise LGInvalidFilesException("Patient not registered at your practice")

    except (ValidationError, ClientError, ValueError) as e:
        logger.error(e)
        raise LGInvalidFilesException(e)


def getting_patient_info_from_pds(nhs_number: str):
    pds_service_class = get_pds_service()
    pds_service = pds_service_class(SSMService())
    pds_response = pds_service.pds_request(nhs_number=nhs_number, retry_on_expired=True)
    if pds_response.status_code == 429:
        logger.error("Got 429 Too Many Requests error from PDS.")
        raise PdsTooManyRequestsException(
            "Failed to validate filename against PDS record due to too many requests"
        )
    elif pds_response.status_code == 404:
        logger.error("Got 404, Could not find the given patient on PDS.")
        raise LGInvalidFilesException(
            "Could not find the given patient on PDS"
        )
    try:
        pds_response.raise_for_status()
    except HTTPError as e:
        logger.error(e)
        raise LGInvalidFilesException("Failed to retrieve patient data from PDS")
    patient = Patient.model_validate(pds_response.json())
    patient_details = patient.get_minimum_patient_details(nhs_number)
    return patient_details


def get_user_ods_code():
    if os.getenv("PDS_FHIR_IS_STUBBED") in ["True", "true"]:
        return "Y12345"
    else:
        ssm_service = SSMService()
        return ssm_service.get_ssm_parameter(SSMParameter.GP_ODS_CODE.value)
