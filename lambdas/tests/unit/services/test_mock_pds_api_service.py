import pytest
from models.pds_models import PatientDetails
from services.mock_pds_service import MockPdsApiService
from utils.exceptions import PatientNotFoundException


def test_fetch_patient_details_valid_returns_PatientDetails():
    nhs_number = "9000000002"

    pds_service = MockPdsApiService()
    actual = pds_service.fetch_patient_details(nhs_number)

    expected = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000002",
        superseded=False,
        restricted=False,
        generalPracticeOds="H81109",
        active=True,
    )

    assert actual == expected


def test_fetch_patient_details_valid_raise_patient_not_found_exception_if_mock_patient_not_exist():
    nhs_number = "987654321"

    pds_service = MockPdsApiService()
    with pytest.raises(PatientNotFoundException):
        pds_service.fetch_patient_details(nhs_number)
