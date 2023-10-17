import pytest
from models.pds_models import PatientDetails
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)

from services.pds_api_service import PdsApiService

class FakeSSMService:
    def __init__(self, *arg, **kwargs):
        pass


pds_service = PdsApiService(FakeSSMService)

def test_handle_response_200_returns_PatientDetails(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 200
    response.json.return_value = PDS_PATIENT

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


def test_handle_response_404_raises_PatientNotFoundException(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 404

    with pytest.raises(PatientNotFoundException):
        pds_service.handle_response(response, nhs_number)


def test_handle_response_400_raises_InvalidResourceIdException(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 400

    with pytest.raises(InvalidResourceIdException):
        pds_service.handle_response(response, nhs_number)


def test_handle_response_catch_all_raises_PdsErrorException(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 500

    with pytest.raises(PdsErrorException):
        pds_service.handle_response(response, nhs_number)

def test_request_new_token_is_call_with_correct_data(mocker):
    mock_jwt_token = "fgjkstjgkld"
    mock_endpoint = "api.endpoint/mock"
    access_token_headers = {"content-type": "application/x-www-form-urlencoded"}
    access_token_data = {
    "grant_type": "client_credentials",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": mock_jwt_token,
}
    mock_post = mocker.patch("requests.post")
    pds_service.request_new_access_token(mock_jwt_token, mock_endpoint)
    mock_post.assert_called_with(url=mock_endpoint, headers=access_token_headers, data=access_token_data)

