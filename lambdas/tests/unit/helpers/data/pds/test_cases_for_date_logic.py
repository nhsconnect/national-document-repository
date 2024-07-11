from typing import Optional

from models.pds_models import Name, Patient
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT


def build_test_name(
    given: list[str] = None,
    family: str = "Smith",
    start: Optional[str] = None,
    end: Optional[str] = None,
    use: str = "usual",
):
    if not given:
        given = ["Jane"]

    period = None
    if start:
        period = {"start": start, "end": end}

    return Name.model_validate(
        {
            "use": use,
            "period": period,
            "given": given,
            "family": family,
        }
    )


def build_test_patient_with_names(names: list[Name]) -> Patient:
    patient = Patient.model_validate(PDS_PATIENT)
    patient.name = names

    return patient
