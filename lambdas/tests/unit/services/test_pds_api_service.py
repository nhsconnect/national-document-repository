import pytest
from models.pds_models import PatientDetails
from requests.models import Response
from services.pds_api_service import PdsApiService
from tests.unit.test_data.utils import load_pds_data
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)

pds_service = PdsApiService()


def test_fetch_patient_details_valid_returns_PatientDetails(mocker):
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 200
    response._content = load_pds_data()[0]

    mocker.patch(
        "services.pds_api_service.PdsApiService.fake_pds_request", return_value=response
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


def test_handle_response_200_returns_PatientDetails():
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 200
    response._content = load_pds_data()[0]

    actual = pds_service.handle_response(response, nhs_number)

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


def test_handle_response_404_raises_PatientNotFoundException():
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 404

    with pytest.raises(PatientNotFoundException):
        pds_service.handle_response(response, nhs_number)


def test_handle_response_400_raises_InvalidResourceIdException():
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 400

    with pytest.raises(InvalidResourceIdException):
        pds_service.handle_response(response, nhs_number)


def test_handle_response_catch_all_raises_PdsErrorException():
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 500

    with pytest.raises(PdsErrorException):
        pds_service.handle_response(response, nhs_number)
