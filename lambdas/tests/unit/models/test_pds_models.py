import pytest
from models.pds_models import PatientDetails
from tests.unit.helpers.data.pds.utils import (create_restricted_patient,
                                               create_unrestricted_patient)
from utils.exceptions import InvalidResourceIdException
from utils.nhs_number_validator import validate_id


def test_validate_id_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_id(nhs_number)

    assert result


def test_validate_id_with_valid_id_raises_InvalidResourceIdException():
    nhs_number = "000000000"

    with pytest.raises(InvalidResourceIdException):
        validate_id(nhs_number)


def test_get_unrestricted_patient_details():
    patient = create_unrestricted_patient()

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
    patient = create_restricted_patient()

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
