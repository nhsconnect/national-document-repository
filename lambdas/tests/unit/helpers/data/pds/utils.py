from models.pds_models import Patient

from .pds_patient_response import PDS_PATIENT, PDS_PATIENT_RESTRICTED


def create_unrestricted_patient():
    return Patient.model_validate(PDS_PATIENT)


def create_restricted_patient():
    return Patient.model_validate(PDS_PATIENT_RESTRICTED)
