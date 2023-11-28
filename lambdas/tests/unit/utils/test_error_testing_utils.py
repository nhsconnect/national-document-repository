from utils.error_testing_utils import (check_manual_error_conditions,
                                       trigger_400)


def test_check_manual_error_conditions_memory(mocker):
    error_type = "MEMORY"
    mock_trigger_memory_error = mocker.patch(
        "utils.error_testing_utils.trigger_memory_error"
    )
    check_manual_error_conditions(error_type)
    mock_trigger_memory_error.assert_called_once()


def test_check_manual_error_conditions_timeout(mocker):
    error_type = "TIMEOUT"
    mock_trigger_timeout_error = mocker.patch(
        "utils.error_testing_utils.trigger_timeout_error"
    )
    check_manual_error_conditions(error_type)
    mock_trigger_timeout_error.assert_called_once()


def test_check_manual_error_conditions_400(mocker):
    error_type = "400"
    mock_trigger_400 = mocker.patch("utils.error_testing_utils.trigger_400")

    check_manual_error_conditions(error_type, "TEST")

    mock_trigger_400.assert_called_once()
    mock_trigger_400.assert_called_with("TEST")


def test_check_manual_error_conditions_500(mocker):
    error_type = "500"
    mock_trigger_500 = mocker.patch("utils.error_testing_utils.trigger_500")

    check_manual_error_conditions(error_type, "POST")

    mock_trigger_500.assert_called_once()
    mock_trigger_500.assert_called_with("POST")


def test_trigger_400():
    expected_status_code = 400
    expected_body = ""

    response = trigger_400("GET")

    actual_status_code = response["statusCode"]
    actual_body = response["body"]

    assert actual_status_code == expected_status_code
    assert actual_body == expected_body
