import pytest
from utils.exceptions import InvalidResourceIdException
from utils.utilities import validate_id


def test_validate_id_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_id(nhs_number)

    assert result


def test_validate_id_with_valid_id_raises_InvalidResourceIdException():
    nhs_number = "000000000"

    with pytest.raises(InvalidResourceIdException):
        validate_id(nhs_number)
