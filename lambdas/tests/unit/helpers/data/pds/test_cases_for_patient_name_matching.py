from datetime import date
from typing import List, NamedTuple

from models.pds_models import PatientDetails
from tests.unit.conftest import TEST_NHS_NUMBER


class PdsNameMatchingTestCase(NamedTuple):
    patient_details: PatientDetails
    patient_name_in_file_name: str
    expect_to_pass: bool


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
    patient_detail = PatientDetails(
        givenName=test_case_dict["pds_name"]["given"],
        familyName=test_case_dict["pds_name"]["family"],
        birthDate=MOCK_DATE_OF_BIRTH,
        nhsNumber=TEST_NHS_NUMBER,
        superseded=False,
        restricted=False,
    )

    test_cases_for_accept = [
        PdsNameMatchingTestCase(
            patient_detail, patient_name_in_file_name=test_name, expect_to_pass=True
        )
        for test_name in test_case_dict["accept"]
    ]
    test_cases_for_reject = [
        PdsNameMatchingTestCase(
            patient_detail,
            patient_name_in_file_name=test_file_name,
            expect_to_pass=False,
        )
        for test_file_name in test_case_dict["reject"]
    ]
    return test_cases_for_accept + test_cases_for_reject
