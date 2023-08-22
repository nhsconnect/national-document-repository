import json

from models.pds_models import Patient


def load_pds_data():
    mock_pds_results: list[dict] = []

    with open("tests/unit/pds_data/pds_patient.json") as f:
        mock_pds_results.append(json.load(f))

    with open("tests/unit/pds_data/pds_patient_restricted.json") as f:
        mock_pds_results.append(json.load(f))

    return mock_pds_results


def create_unrestricted_patient():
    mock_pds_data = load_pds_data()
    return Patient.model_validate(mock_pds_data[0])


def create_restricted_patient():
    mock_pds_data = load_pds_data()
    return Patient.model_validate(mock_pds_data[1])
