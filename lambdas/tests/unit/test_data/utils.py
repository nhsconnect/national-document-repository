import json

from models.pds_models import Patient


def load_pds_data():
    mock_pds_results: list[dict] = []

    with open("tests/unit/test_data/pds_patient.json") as f:
        mock_pds_results.append(json.load(f))

    with open("tests/unit/test_data/pds_patient_restricted.json") as f:
        mock_pds_results.append(json.load(f))

    return mock_pds_results


def create_unrestricted_patient():
    mock_pds_data = load_pds_data()
    return Patient.model_validate(mock_pds_data[0])


def create_restricted_patient():
    mock_pds_data = load_pds_data()
    return Patient.model_validate(mock_pds_data[1])


def load_ods_response_data():
    mock_responses = {}

    test_cases = [
        "with_valid_gp_role",
        "with_valid_pcse_role",
        "with_multiple_valid_roles",
        "with_no_valid_roles",
    ]

    for test_case in test_cases:
        with open(f"tests/unit/test_data/ods_response_{test_case}.json") as f:
            mock_responses[test_case] = json.load(f)

    return mock_responses
