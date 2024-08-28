import pytest

from enums.patient_ods_inactive_status import PatientOdsInactiveStatus
from utils.ods_utils import is_ods_code_active


@pytest.mark.parametrize(
    "ods_code,expected",
    [
        ["H81109", True],
        [PatientOdsInactiveStatus.SUSPENDED, False],
        [PatientOdsInactiveStatus.DECEASED, False],
        ["", False],
        [None, False]
    ]
)
def test_is_ods_code_active(ods_code, expected):
    actual = is_ods_code_active(ods_code)

    assert actual == expected