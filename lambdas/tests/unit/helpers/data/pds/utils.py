from models.pds_models import Patient


def create_unrestricted_patient(pds_response):
    return Patient.model_validate(pds_response)


def create_restricted_patient(pds_response):
    return Patient.model_validate(pds_response)
