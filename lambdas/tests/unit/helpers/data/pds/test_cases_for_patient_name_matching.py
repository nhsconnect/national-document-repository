import copy
from datetime import date
from typing import List, NamedTuple

from models.pds_models import Patient
from tests.unit.helpers.data.pds.pds_patient_response import PDS_PATIENT


class PdsNameMatchingTestCase(NamedTuple):
    patient_details: Patient
    patient_name_in_file_name: str
    should_accept_name: bool


TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME = {
    "pds_name": {"family": "Smith Anderson", "given": ["Jane", "Bob"]},
    "accept": [
        "Jane Bob Smith Anderson",
        "Jane Smith Anderson",
        "Jane B Smith Anderson",
    ],
    "reject": [
        "Bob Smith Anderson",
        "Jane Smith",
        "Jane Anderson",
        "Jane Anderson Smith",
    ],
}

TEST_CASES_FOR_FAMILY_NAME_WITH_HYPHEN = {
    "pds_name": {"family": "Smith-Anderson", "given": ["Jane"]},
    "accept": ["Jane Smith-Anderson"],
    "reject": ["Jane Smith Anderson", "Jane Smith", "Jane Anderson"],
}

TEST_CASES_FOR_TWO_WORDS_GIVEN_NAME = {
    "pds_name": {"family": "Smith", "given": ["Jane Bob"]},
    "accept": ["Jane Bob Smith"],
    "reject": ["Jane Smith", "Jane B Smith", "Jane-Bob Smith", "Bob Smith"],
}

TEST_CASES_FOR_TWO_WORDS_FAMILY_NAME_AND_GIVEN_NAME = {
    "pds_name": {"family": "Smith Anderson", "given": ["Jane Bob"]},
    "accept": ["Jane Bob Smith Anderson"],
    "reject": [
        "Jane Smith Anderson",
        "Bob Smith Anderson",
        "Jane B Smith Anderson",
        "Jane Bob Smith",
        "Jane Bob Anderson",
    ],
}


MOCK_DATE_OF_BIRTH = date(2010, 10, 22)


def load_test_cases(test_case_dict: dict) -> List[PdsNameMatchingTestCase]:
    pds_response_patient = copy.deepcopy(PDS_PATIENT)
    pds_response_patient["name"][0]["given"] = test_case_dict["pds_name"]["given"]
    pds_response_patient["name"][0]["family"] = test_case_dict["pds_name"]["family"]

    patient = Patient.model_validate(pds_response_patient)

    test_cases_for_accept = [
        PdsNameMatchingTestCase(
            patient, patient_name_in_file_name=test_name, should_accept_name=True
        )
        for test_name in test_case_dict["accept"]
    ]
    test_cases_for_reject = [
        PdsNameMatchingTestCase(
            patient,
            patient_name_in_file_name=test_file_name,
            should_accept_name=False,
        )
        for test_file_name in test_case_dict["reject"]
    ]
    return test_cases_for_accept + test_cases_for_reject
