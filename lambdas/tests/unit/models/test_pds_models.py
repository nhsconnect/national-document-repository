import pytest
from freezegun import freeze_time
from models.pds_models import PatientDetails
from pydantic import ValidationError
from tests.unit.helpers.data.pds.pds_patient_response import (
    PDS_PATIENT,
    PDS_PATIENT_NO_GIVEN_NAME_IN_CURRENT_NAME,
    PDS_PATIENT_NO_GIVEN_NAME_IN_HISTORIC_NAME,
    PDS_PATIENT_NO_PERIOD_IN_NAME_MODEL,
    PDS_PATIENT_RESTRICTED,
    PDS_PATIENT_WITH_GP_END_DATE,
    PDS_PATIENT_WITHOUT_ACTIVE_GP,
    PDS_PATIENT_WITHOUT_ADDRESS,
)
from tests.unit.helpers.data.pds.utils import create_patient
from utils.utilities import validate_nhs_number

EXPECTED_PARSED_PATIENT_BASE_CASE = PatientDetails(
    givenName=["Jane"],
    familyName="Smith",
    birthDate="2010-10-22",
    postalCode="LS1 6AE",
    nhsNumber="9000000009",
    superseded=False,
    restricted=False,
    generalPracticeOds="Y12345",
    active=True,
)


def test_validate_nhs_number_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_nhs_number(nhs_number)

    assert result


def test_get_unrestricted_patient_details():
    patient = create_patient(PDS_PATIENT)

    result = patient.get_patient_details(patient.id)

    assert EXPECTED_PARSED_PATIENT_BASE_CASE == result


def test_get_restricted_patient_details():
    patient = create_patient(PDS_PATIENT_RESTRICTED)

    expected_patient_details = PatientDetails(
        givenName=["Janet"],
        familyName="Smythe",
        birthDate="2010-10-22",
        postalCode="",
        nhsNumber="9000000025",
        superseded=False,
        restricted=True,
        generalPracticeOds="",
        active=False,
    )

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


def test_get_minimum_patient_details():
    patient = create_patient(PDS_PATIENT)

    expected_patient_details = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        generalPracticeOds="Y12345",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
    )

    result = patient.get_minimum_patient_details(patient.id)

    assert expected_patient_details == result


@freeze_time("2024-12-31")
def test_gp_ods_empty_when_gp_end_date_indicates_inactive():
    patient = create_patient(PDS_PATIENT_WITH_GP_END_DATE)

    response = patient.get_minimum_patient_details(patient.id)

    assert response.general_practice_ods == ""


def test_raise_error_when_no_gp_in_response():
    patient = create_patient(PDS_PATIENT_WITHOUT_ACTIVE_GP)

    response = patient.get_minimum_patient_details(patient.id)

    assert response.general_practice_ods == ""


@freeze_time("2021-12-31")
def test_not_raise_error_when_gp_end_date_is_today():
    try:
        patient = create_patient(PDS_PATIENT_WITH_GP_END_DATE)
        patient.get_minimum_patient_details(patient.id)
    except ValueError:
        assert False, "No active GP practice for the patient"


@freeze_time("2019-12-31")
def test_not_raise_error_when_gp_end_date_is_in_the_future():
    try:
        patient = create_patient(PDS_PATIENT_WITH_GP_END_DATE)
        patient.get_minimum_patient_details(patient.id)
    except ValueError:
        assert False, "No active GP practice for the patient"


def test_get_minimum_patient_details_missing_address():
    patient = create_patient(PDS_PATIENT_WITHOUT_ADDRESS)

    expected_patient_details = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
        generalPracticeOds="Y12345",
        active=True,
    )

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


def test_patient_without_period_in_name_model_can_be_processed_successfully():
    patient = create_patient(PDS_PATIENT_NO_PERIOD_IN_NAME_MODEL)

    result = patient.get_patient_details(patient.id)

    assert EXPECTED_PARSED_PATIENT_BASE_CASE == result


def test_patient_without_given_name_in_historic_name_can_be_processed_successfully():
    patient = create_patient(PDS_PATIENT_NO_GIVEN_NAME_IN_HISTORIC_NAME)

    result = patient.get_patient_details(patient.id)

    assert EXPECTED_PARSED_PATIENT_BASE_CASE == result


def test_patient_without_given_name_in_current_name_raise_error():
    with pytest.raises(ValidationError):
        patient = create_patient(PDS_PATIENT_NO_GIVEN_NAME_IN_CURRENT_NAME)
        patient.get_patient_details(patient.id)
