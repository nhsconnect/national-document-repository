import pytest
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from services.back_channel_logout_service import BackChannelLogoutService
from utils.exceptions import AuthorisationException, LogoutFailureException


@pytest.fixture()
def mock_back_channel_logout_service(mocker, monkeypatch, set_env):
    patched_back_channel_logout_service = BackChannelLogoutService()
    mocker.patch.object(patched_back_channel_logout_service, "oidc_service")
    mocker.patch.object(patched_back_channel_logout_service, "dynamodb_service")
    yield patched_back_channel_logout_service


def test_remove_session_from_dynamo_db(mock_back_channel_logout_service, mocker):
    mock_delete = mocker.patch("services.dynamo_service.DynamoDBService.delete_item")

    mock_back_channel_logout_service.remove_session_from_dynamo_db("session_id_test")

    mock_delete.assert_called_with(
        key={"NDRSessionId": "session_id_test"}, table_name="test_dynamo"
    )


def test_finding_session_id_by_sid_return_session(
    mock_back_channel_logout_service, mocker
):
    scan_response = {"Items": [{"NDRSessionId": "ndr_id_test"}]}
    mock_find = mocker.patch(
        "services.dynamo_service.DynamoDBService.scan_table", return_value=scan_response
    )
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_find.assert_called_with(table_name="test_dynamo", filter_expression=filter_sid)
    assert actual == "ndr_id_test"


def test_finding_session_id_by_sid_return_none(
    mock_back_channel_logout_service, mocker
):
    scan_response = {}
    mock_find = mocker.patch(
        "services.dynamo_service.DynamoDBService.scan_table", return_value=scan_response
    )
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_find.assert_called_with(table_name="test_dynamo", filter_expression=filter_sid)
    assert actual is None


def test_finding_session_id_with_return_empty_items(
    mock_back_channel_logout_service, mocker
):
    scan_response = {"Items": []}
    mock_find = mocker.patch(
        "services.dynamo_service.DynamoDBService.scan_table", return_value=scan_response
    )
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_find.assert_called_with(table_name="test_dynamo", filter_expression=filter_sid)
    assert actual is None


def test_finding_session_id_with_return_different_items(
    mock_back_channel_logout_service, mocker
):
    scan_response = {"Items": [{"NotNDRSessionId": "not_ndr_id_test"}]}
    mock_find = mocker.patch(
        "services.dynamo_service.DynamoDBService.scan_table", return_value=scan_response
    )
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_find.assert_called_with(table_name="test_dynamo", filter_expression=filter_sid)
    assert actual is None


def test_finding_session_id_with_return_string_items(
    mock_back_channel_logout_service, mocker
):
    scan_response = {"Items": "long_string"}
    mock_find = mocker.patch(
        "services.dynamo_service.DynamoDBService.scan_table", return_value=scan_response
    )
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_find.assert_called_with(table_name="test_dynamo", filter_expression=filter_sid)
    assert actual is None


def test_back_channel_logout_handler_boto_error_raise_error(
    mocker, mock_back_channel_logout_service
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mocker.patch("services.oidc_service.OidcService.set_up_oidc_parameters")
    mocker.patch(
        "services.oidc_service.OidcService.validate_and_decode_token",
        return_value=mock_decoded_token,
    )
    mocker.patch(
        "services.back_channel_logout_service.BackChannelLogoutService.finding_session_id_by_sid",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )
    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)


def test_back_channel_logout_handler_invalid_jwt_raise_error(
    mocker, mock_back_channel_logout_service
):
    mock_token = "mock_token"
    mocker.patch("services.oidc_service.OidcService.set_up_oidc_parameters")
    mocker.patch(
        "services.oidc_service.OidcService.validate_and_decode_token",
        side_effect=AuthorisationException(None, None),
    )
    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)


def test_back_channel_logout_handler_remove_dynamo_failed_raise_error(
    mocker, mock_back_channel_logout_service
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mock_set_up = mocker.patch(
        "services.oidc_service.OidcService.set_up_oidc_parameters"
    )
    mock_validate_token = mocker.patch(
        "services.oidc_service.OidcService.validate_and_decode_token",
        return_value=mock_decoded_token,
    )
    mock_find_session = mocker.patch(
        "services.back_channel_logout_service.BackChannelLogoutService.finding_session_id_by_sid",
        return_value=mock_session_id,
    )
    mocker.patch(
        "services.back_channel_logout_service.BackChannelLogoutService.remove_session_from_dynamo_db",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )
    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)

    mock_set_up.assert_called_once()
    mock_validate_token.assert_called_with(mock_token)
    mock_find_session.assert_called_with(mock_session_id)


def test_back_channel_logout_handler_oidc_set_up_raise_error(
    mocker, mock_back_channel_logout_service
):
    mock_token = "mock_token"
    mock_set_up = mocker.patch(
        "services.oidc_service.OidcService.set_up_oidc_parameters",
        side_effect=ClientError(
            {"Error": {"Code": "500", "Message": "mocked error"}}, "test"
        ),
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)
    mock_set_up.assert_called_once()


def test_back_channel_logout_handler_no_sid_in_token_failed_raise_error(
    mocker, mock_back_channel_logout_service
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"not_sid": mock_session_id}
    mock_set_up = mocker.patch(
        "services.oidc_service.OidcService.set_up_oidc_parameters"
    )
    mock_validate_token = mocker.patch(
        "services.oidc_service.OidcService.validate_and_decode_token",
        return_value=mock_decoded_token,
    )
    mock_find_session = mocker.patch(
        "services.back_channel_logout_service.BackChannelLogoutService.finding_session_id_by_sid"
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)

    mock_set_up.assert_called_once()
    mock_validate_token.assert_called_with(mock_token)
    mock_find_session.assert_not_called()


def test_back_channel_logout_handler_no_session_id_raise_error(
    mocker, mock_back_channel_logout_service
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}
    mock_set_up = mocker.patch(
        "services.oidc_service.OidcService.set_up_oidc_parameters"
    )
    mock_validate_token = mocker.patch(
        "services.oidc_service.OidcService.validate_and_decode_token",
        return_value=mock_decoded_token,
    )
    mock_find_session = mocker.patch(
        "services.back_channel_logout_service.BackChannelLogoutService.finding_session_id_by_sid",
        return_value=None,
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)

    mock_set_up.assert_called_once()
    mock_validate_token.assert_called_with(mock_token)
    mock_find_session.assert_called_with(mock_session_id)


def test_back_channel_logout_handler_valid_jwt_no_error_raise_if_session_exists(
    mocker, mock_back_channel_logout_service, monkeypatch, context
):
    try:
        mock_token = "mock_token"
        mock_session_id = "mock_session_id"
        mock_decoded_token = {"sid": mock_session_id}
        mock_set_up = mocker.patch(
            "services.oidc_service.OidcService.set_up_oidc_parameters"
        )
        mock_validate_token = mocker.patch(
            "services.oidc_service.OidcService.validate_and_decode_token",
            return_value=mock_decoded_token,
        )
        mock_find_session = mocker.patch(
            "services.back_channel_logout_service.BackChannelLogoutService.finding_session_id_by_sid",
            return_value=mock_session_id,
        )
        mocker.patch(
            "services.back_channel_logout_service.BackChannelLogoutService.remove_session_from_dynamo_db"
        )

        mock_back_channel_logout_service.logout_handler(mock_token)

        mock_set_up.assert_called_once()
        mock_validate_token.assert_called_with(mock_token)
        mock_find_session.assert_called_with(mock_session_id)

    except LogoutFailureException as e:
        assert False, e
