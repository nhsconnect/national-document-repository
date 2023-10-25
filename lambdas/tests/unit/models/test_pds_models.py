import pytest
from freezegun import freeze_time

from models.pds_models import PatientDetails
from tests.unit.helpers.data.pds.utils import (
    create_restricted_patient,
    create_unrestricted_patient,
)
from tests.unit.helpers.data.pds.pds_patient_response import (
    PDS_PATIENT_WITHOUT_ACTIVE_GP,
    PDS_PATIENT_WITH_GP_END_DATE,
    PDS_PATIENT,
    PDS_PATIENT_RESTRICTED,
)
from utils.exceptions import InvalidResourceIdException
from utils.utilities import validate_id


def test_validate_id_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_id(nhs_number)

    assert result


def test_validate_id_with_valid_id_raises_InvalidResourceIdException():
    nhs_number = "000000000"

    with pytest.raises(InvalidResourceIdException):
        validate_id(nhs_number)


def test_get_unrestricted_patient_details():
    patient = create_unrestricted_patient(PDS_PATIENT)

    expected_patient_details = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
    )

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


def test_get_restricted_patient_details():
    patient = create_restricted_patient(PDS_PATIENT_RESTRICTED)

    expected_patient_details = PatientDetails(
        givenName=["Janet"],
        familyName="Smythe",
        birthDate="2010-10-22",
        postalCode="",
        nhsNumber="9000000025",
        superseded=False,
        restricted=True,
    )

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


def test_get_minimum_patient_details():
    patient = create_unrestricted_patient(PDS_PATIENT)

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
def test_raise_error_when_gp_end_date_indicates_inactive():
    patient = create_unrestricted_patient(PDS_PATIENT_WITH_GP_END_DATE)

    with pytest.raises(ValueError):
        patient.get_minimum_patient_details(patient.id)


def test_raise_error_when_no_gp_in_response():
    patient = create_unrestricted_patient(PDS_PATIENT_WITHOUT_ACTIVE_GP)

    with pytest.raises(ValueError):
        patient.get_minimum_patient_details(patient.id)


@freeze_time("2021-12-31")
def test_not_raise_error_when_gp_end_date_is_today():
    try:
        patient = create_unrestricted_patient(PDS_PATIENT_WITH_GP_END_DATE)
        patient.get_minimum_patient_details(patient.id)
    except ValueError:
        assert False, "No active GP practice for the patient"


@freeze_time("2019-12-31")
def test_not_raise_error_when_gp_end_date_is_in_the_future():
    try:
        patient = create_unrestricted_patient(PDS_PATIENT_WITH_GP_END_DATE)
        patient.get_minimum_patient_details(patient.id)
    except ValueError:
        assert False, "No active GP practice for the patient"
