import pytest
from utils.exceptions import InvalidResourceIdException
from utils.utilities import (
    camelize_dict,
    flatten,
    get_file_key_from_s3_url,
    redact_id_to_last_4_chars,
    validate_nhs_number,
)


def test_validate_nhs_number_with_valid_id_returns_true():
    nhs_number = "0000000000"

    result = validate_nhs_number(nhs_number)

    assert result


def test_validate_nhs_number_with_valid_id_raises_InvalidResourceIdException():
    nhs_number = "000000000"

    with pytest.raises(InvalidResourceIdException):
        validate_nhs_number(nhs_number)


def test_decapitalise_keys():
    test_dict = {"FileName": "test", "VirusScannerResult": "test"}

    expected = {"fileName": "test", "virusScannerResult": "test"}

    actual = camelize_dict(test_dict)

    assert actual == expected


def test_redact_id():
    mock_session_id = "1234532532432"
    expected = "2432"

    actual = redact_id_to_last_4_chars(mock_session_id)

    assert expected == actual


def test_get_file_key_from_s3_url():
    test_url = "s3://test-s3-bucket/9000000009/user-upload/arf/3575f1ab-e7ae-4edf-958b-410ac0d42461"
    expected = "9000000009/user-upload/arf/3575f1ab-e7ae-4edf-958b-410ac0d42461"
    actual = get_file_key_from_s3_url(test_url)

    assert actual == expected


def test_flatten_reduce_one_level_of_nesting_given_a_nested_list():
    nested_list = [["a", "b", "c"], ["d", "e"], ["f"], ["a"]]
    expected = ["a", "b", "c", "d", "e", "f", "a"]

    actual = flatten(nested_list)

    assert actual == expected
