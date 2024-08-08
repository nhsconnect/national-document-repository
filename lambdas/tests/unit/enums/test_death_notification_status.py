import pytest
from enums.death_notification_status import DeathNotificationStatus

test_cases = [
    ("1", DeathNotificationStatus.INFORMAL),
    ("2", DeathNotificationStatus.FORMAL),
    ("U", DeathNotificationStatus.REMOVED),
    ("OTHER", None),
]


@pytest.mark.parametrize(["code", "expected"], test_cases)
def test_from_code(code, expected):
    actual = DeathNotificationStatus.from_code(code)

    assert actual == expected
