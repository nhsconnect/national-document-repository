from freezegun import freeze_time
from models.pds_models import Name, PatientDetails
from tests.unit.conftest import EXPECTED_PARSED_PATIENT_BASE_CASE
from tests.unit.helpers.data.pds.pds_patient_response import (
    PDS_PATIENT,
    PDS_PATIENT_NO_GIVEN_NAME_IN_CURRENT_NAME,
    PDS_PATIENT_NO_GIVEN_NAME_IN_HISTORIC_NAME,
    PDS_PATIENT_NO_PERIOD_IN_GENERAL_PRACTITIONER_IDENTIFIER,
    PDS_PATIENT_NO_PERIOD_IN_NAME_MODEL,
    PDS_PATIENT_RESTRICTED,
    PDS_PATIENT_WITH_GP_END_DATE,
    PDS_PATIENT_WITHOUT_ACTIVE_GP,
    PDS_PATIENT_WITHOUT_ADDRESS,
)
from tests.unit.helpers.data.pds.test_cases_for_date_logic import (
    build_test_name,
    build_test_patient_with_names,
)
from tests.unit.helpers.data.pds.utils import create_patient
from utils.utilities import validate_nhs_number


def test_validate_nhs_number_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_nhs_number(nhs_number)

    assert result


def test_get_unrestricted_patient_details():
    patient = create_patient(PDS_PATIENT)

    result = patient.get_patient_details(patient.id)

    assert EXPECTED_PARSED_PATIENT_BASE_CASE == result


def test_get_restricted_patient_details():
    patient = create_patient(PDS_PATIENT_RESTRICTED)

    expected_patient_details = PatientDetails(
        givenName=["Janet"],
        familyName="Smythe",
        birthDate="2010-10-22",
        postalCode="",
        nhsNumber="9000000025",
        superseded=False,
        restricted=True,
        generalPracticeOds="",
        active=False,
    )

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


def test_get_minimum_patient_details():
    patient = create_patient(PDS_PATIENT)

    expected_patient_details = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        generalPracticeOds="Y12345",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
    )

    result = patient.get_minimum_patient_details(patient.id)

    assert expected_patient_details == result


@freeze_time("2024-12-31")
def test_gp_ods_empty_when_gp_end_date_indicates_inactive():
    patient = create_patient(PDS_PATIENT_WITH_GP_END_DATE)

    response = patient.get_minimum_patient_details(patient.id)

    assert response.general_practice_ods == ""


def test_not_raise_error_when_no_gp_in_response():
    patient = create_patient(PDS_PATIENT_WITHOUT_ACTIVE_GP)

    response = patient.get_minimum_patient_details(patient.id)

    assert response.general_practice_ods == ""


@freeze_time("2021-12-31")
def test_not_raise_error_when_gp_end_date_is_today():
    try:
        patient = create_patient(PDS_PATIENT_WITH_GP_END_DATE)
        patient.get_minimum_patient_details(patient.id)
    except ValueError:
        assert False, "No active GP practice for the patient"


@freeze_time("2019-12-31")
def test_not_raise_error_when_gp_end_date_is_in_the_future():
    try:
        patient = create_patient(PDS_PATIENT_WITH_GP_END_DATE)
        patient.get_minimum_patient_details(patient.id)
    except ValueError:
        assert False, "No active GP practice for the patient"


def test_get_minimum_patient_details_missing_address():
    patient = create_patient(PDS_PATIENT_WITHOUT_ADDRESS)

    expected_patient_details = PatientDetails(
        givenName=["Jane"],
        familyName="Smith",
        birthDate="2010-10-22",
        postalCode="",
        nhsNumber="9000000009",
        superseded=False,
        restricted=False,
        generalPracticeOds="Y12345",
        active=True,
    )

    result = patient.get_patient_details(patient.id)

    assert expected_patient_details == result


def test_patient_without_period_in_name_model_can_be_processed_successfully():
    patient = create_patient(PDS_PATIENT_NO_PERIOD_IN_NAME_MODEL)

    result = patient.get_patient_details(patient.id)

    assert EXPECTED_PARSED_PATIENT_BASE_CASE == result


def test_patient_without_given_name_in_historic_name_can_be_processed_successfully():
    patient = create_patient(PDS_PATIENT_NO_GIVEN_NAME_IN_HISTORIC_NAME)

    result = patient.get_patient_details(patient.id)

    assert EXPECTED_PARSED_PATIENT_BASE_CASE == result


def test_patient_without_given_name_in_current_name_logs_a_warning_and_process_successfully(
    caplog,
):
    patient = create_patient(PDS_PATIENT_NO_GIVEN_NAME_IN_CURRENT_NAME)

    expected = EXPECTED_PARSED_PATIENT_BASE_CASE.model_copy(update={"given_name": [""]})
    result = patient.get_patient_details(patient.id)

    assert expected == result

    expected_log = "The given name of patient is empty."
    actual_log = caplog.records[-1].msg
    assert expected_log == actual_log


def test_patient_without_period_in_general_practitioner_identifier_can_be_processed_successfully():
    patient = create_patient(PDS_PATIENT_NO_PERIOD_IN_GENERAL_PRACTITIONER_IDENTIFIER)

    expected = EXPECTED_PARSED_PATIENT_BASE_CASE
    result = patient.get_patient_details(patient.id)

    assert expected == result


BaseTestName = Name.model_validate(
    {
        "use": "usual",
        "period": {"start": "2023-01-01", "end": "2025-12-31"},
        "given": ["Jane"],
        "family": "Smith",
    }
)


@freeze_time("2024-01-01")
def test_name_is_currently_in_use_return_false_for_expired_name():
    test_name = build_test_name(start="2023-01-01", end="2023-06-01")
    expected = False
    actual = test_name.is_currently_in_use()

    assert actual == expected


@freeze_time("2024-01-01")
def test_name_is_currently_in_use_return_false_for_name_not_started_yet():
    test_name = build_test_name(start="2024-02-01", end="2024-06-01")
    expected = False
    actual = test_name.is_currently_in_use()

    assert actual == expected


@freeze_time("2024-01-01")
def test_name_is_currently_in_use_return_true_when_name_period_includes_today():
    test_name = build_test_name(start="2023-12-31", end="2024-02-01")
    expected = True
    actual = test_name.is_currently_in_use()

    assert actual == expected


@freeze_time("2024-01-01")
def test_name_is_currently_in_use_return_false_for_name_without_a_period_field():
    test_name = build_test_name(start=None, end=None)
    assert test_name.period is None

    expected = False
    actual = test_name.is_currently_in_use()

    assert actual == expected


@freeze_time("2024-01-01")
def test_name_is_currently_in_use_can_handle_name_with_no_end_in_period():
    test_name = build_test_name(start="2023-12-31", end=None)
    assert test_name.period.end is None

    expected = True
    actual = test_name.is_currently_in_use()

    assert actual == expected


@freeze_time("2024-01-01")
def test_name_is_currently_in_use_return_false_for_nickname_or_old_name():
    test_nickname = build_test_name(
        use="nickname", start="2023-01-01", end="2024-12-31"
    )
    test_old_name = build_test_name(use="old", start="2023-01-01", end="2024-12-31")

    assert test_nickname.is_currently_in_use() is False
    assert test_old_name.is_currently_in_use() is False


@freeze_time("2024-01-01")
def test_get_most_recent_name_return_the_name_with_most_recent_start_date():
    name_1 = build_test_name(start="1990-01-01", end=None, given=["Jane"])
    name_2 = build_test_name(start="2010-02-14", end=None, given=["Jones"])
    name_3 = build_test_name(start="2000-03-25", end=None, given=["Bob"])
    expired_name = build_test_name(
        start="2020-04-05", end="2022-07-01", given=["Alice"]
    )
    nickname = build_test_name(
        use="nickname", start="2023-01-01", end=None, given=["Janie"]
    )
    future_name = build_test_name(start="2047-01-01", end=None, given=["Neo Jane"])

    test_patient = build_test_patient_with_names(
        [name_1, name_2, name_3, expired_name, nickname, future_name]
    )

    expected = name_2
    actual = test_patient.get_most_recent_name()

    assert actual == expected
