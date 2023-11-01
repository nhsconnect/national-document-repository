from models.pds_models import Patient


def create_patient(pds_response):
    return Patient.model_validate(pds_response)
