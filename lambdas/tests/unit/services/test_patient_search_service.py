import json

import pytest
from models.pds_models import PatientDetails
from requests import Response
from services.patient_search_service import PatientSearch
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT
from utils.exceptions import (InvalidResourceIdException,
                              PatientNotFoundException, PdsErrorException)

search_service = PatientSearch()


def test_handle_response_200_returns_PatientDetails():
    nhs_number = "9000000025"

    response = Response()
    response.status_code = 200
    response._content = json.dumps(PDS_PATIENT).encode("utf-8")

    actual = search_service.handle_response(response, nhs_number)

    expected = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="LS1 6AE",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
        generalPracticeOds="Y12345",
        active=True
    )

    assert actual == expected


def test_handle_response_404_raises_PatientNotFoundException(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 404

    with pytest.raises(PatientNotFoundException):
        search_service.handle_response(response, nhs_number)


def test_handle_response_400_raises_InvalidResourceIdException(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 400

    with pytest.raises(InvalidResourceIdException):
        search_service.handle_response(response, nhs_number)


def test_handle_response_catch_all_raises_PdsErrorException(mocker):
    nhs_number = "9000000025"

    response = mocker.MagicMock()
    response.status_code = 500

    with pytest.raises(PdsErrorException):
        search_service.handle_response(response, nhs_number)
