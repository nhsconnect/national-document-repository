import pytest
from models.pds_models import PatientDetails
from requests.models import Response
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)

from services.mock_pds_service import MockPdsApiService

pds_service = MockPdsApiService()

def test_fetch_patient_details_valid_returns_PatientDetails(mocker):
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 200
    response._content = PDS_PATIENT

    mocker.patch(
        "services.mock_pds_service.MockPdsApiService.fake_pds_request", return_value=response
    )

    actual = pds_service.fetch_patient_details(nhs_number)

    expected = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
    )

    assert actual == expected


def test_fetch_patient_details_invalid_nhs_number_raises_InvalidResourceIdException():
    nhs_number = "000000000"

    with pytest.raises(InvalidResourceIdException):
        pds_service.fetch_patient_details(nhs_number)

