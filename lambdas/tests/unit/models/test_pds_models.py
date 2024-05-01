from freezegun import freeze_time
from models.pds_models import PatientDetails
from tests.unit.helpers.data.pds.pds_patient_response import (
    PDS_PATIENT,
    PDS_PATIENT_RESTRICTED,
    PDS_PATIENT_WITH_GP_END_DATE,
    PDS_PATIENT_WITHOUT_ACTIVE_GP,
)
from tests.unit.helpers.data.pds.utils import create_patient
from utils.utilities import validate_nhs_number


def test_validate_nhs_number_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_nhs_number(nhs_number)

    assert result


def test_get_unrestricted_patient_details():
    patient = create_patient(PDS_PATIENT)

    expected_patient_details = PatientDetails(
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

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


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
        generalPracticeOds=None,
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
