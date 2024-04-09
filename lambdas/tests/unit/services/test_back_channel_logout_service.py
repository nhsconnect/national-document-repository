import pytest
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from services.back_channel_logout_service import BackChannelLogoutService
from utils.exceptions import AuthorisationException, LogoutFailureException


@pytest.fixture()
def mock_back_channel_logout_service(mocker, set_env):
    mocker.patch("services.back_channel_logout_service.OidcService")
    mocker.patch("services.back_channel_logout_service.DynamoDBService")
    patched_back_channel_logout_service = BackChannelLogoutService()
    yield patched_back_channel_logout_service


@pytest.fixture
def mock_dynamo(mocker, mock_back_channel_logout_service):
    mocker.patch.object(
        mock_back_channel_logout_service.dynamodb_service, "delete_item"
    )
    mocker.patch.object(mock_back_channel_logout_service.dynamodb_service, "scan_table")
    yield mock_back_channel_logout_service.dynamodb_service


@pytest.fixture
def mock_finding_session_id_by_sid(mocker, mock_back_channel_logout_service):
    yield mocker.patch.object(
        mock_back_channel_logout_service,
        "finding_session_id_by_sid",
    )


@pytest.fixture
def mock_remove_session_from_dynamo_db(mocker, mock_back_channel_logout_service):
    yield mocker.patch.object(
        mock_back_channel_logout_service, "remove_session_from_dynamo_db"
    )


def test_remove_session_from_dynamo_db(mock_back_channel_logout_service, mock_dynamo):
    mock_back_channel_logout_service.remove_session_from_dynamo_db("session_id_test")

    mock_dynamo.delete_item.assert_called_with(
        key={"NDRSessionId": "session_id_test"}, table_name="test_dynamo"
    )


def test_finding_session_id_by_sid_return_session(
    mock_back_channel_logout_service, mock_dynamo
):
    scan_response = {"Items": [{"NDRSessionId": "ndr_id_test"}]}
    mock_dynamo.scan_table.return_value = scan_response
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_dynamo.scan_table.assert_called_with(
        table_name="test_dynamo", filter_expression=filter_sid
    )
    assert actual == "ndr_id_test"


def test_finding_session_id_by_sid_return_none(
    mock_back_channel_logout_service, mock_dynamo
):
    scan_response = {}
    mock_dynamo.scan_table.return_value = scan_response
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_dynamo.scan_table.assert_called_with(
        table_name="test_dynamo", filter_expression=filter_sid
    )
    assert actual is None


def test_finding_session_id_with_return_empty_items(
    mock_back_channel_logout_service, mock_dynamo
):
    scan_response = {"Items": []}
    mock_dynamo.scan_table.return_value = scan_response
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_dynamo.scan_table.assert_called_with(
        table_name="test_dynamo", filter_expression=filter_sid
    )
    assert actual is None


def test_finding_session_id_with_return_different_items(
    mock_back_channel_logout_service, mock_dynamo
):
    scan_response = {"Items": [{"NotNDRSessionId": "not_ndr_id_test"}]}
    mock_dynamo.scan_table.return_value = scan_response
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_dynamo.scan_table.assert_called_with(
        table_name="test_dynamo", filter_expression=filter_sid
    )
    assert actual is None


def test_finding_session_id_with_return_string_items(
    mock_back_channel_logout_service, mock_dynamo
):
    scan_response = {"Items": "long_string"}
    mock_dynamo.scan_table.return_value = scan_response
    filter_sid = Attr("sid").eq("session_id_sid")

    actual = mock_back_channel_logout_service.finding_session_id_by_sid(
        "session_id_sid"
    )

    mock_dynamo.scan_table.assert_called_with(
        table_name="test_dynamo", filter_expression=filter_sid
    )
    assert actual is None


def test_back_channel_logout_handler_boto_error_raise_error(
    mock_back_channel_logout_service, mock_finding_session_id_by_sid
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}

    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.return_value = (
        mock_decoded_token
    )
    mock_finding_session_id_by_sid.side_effect = (
        ClientError({"Error": {"Code": "500", "Message": "mocked error"}}, "test"),
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)


def test_back_channel_logout_handler_invalid_jwt_raise_error(
    mock_back_channel_logout_service,
):
    mock_token = "mock_token"
    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.side_effect = (
        AuthorisationException()
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)


def test_back_channel_logout_handler_remove_dynamo_failed_raise_error(
    mock_back_channel_logout_service,
    mock_finding_session_id_by_sid,
    mock_remove_session_from_dynamo_db,
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}

    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.return_value = (
        mock_decoded_token
    )
    mock_finding_session_id_by_sid.return_value = mock_session_id
    mock_remove_session_from_dynamo_db.side_effect = (
        ClientError({"Error": {"Code": "500", "Message": "mocked error"}}, "test"),
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)

    mock_back_channel_logout_service.oidc_service.set_up_oidc_parameters.assert_called_once()
    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.assert_called_with(
        mock_token
    )
    mock_finding_session_id_by_sid.assert_called_with(mock_session_id)


def test_back_channel_logout_handler_oidc_set_up_raise_error(
    mock_back_channel_logout_service,
):
    mock_token = "mock_token"
    mock_back_channel_logout_service.oidc_service.set_up_oidc_parameters.side_effect = (
        ClientError({"Error": {"Code": "500", "Message": "mocked error"}}, "test")
    )

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)
    mock_back_channel_logout_service.oidc_service.set_up_oidc_parameters.assert_called_once()


def test_back_channel_logout_handler_no_sid_in_token_failed_raise_error(
    mock_back_channel_logout_service, mock_finding_session_id_by_sid
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"not_sid": mock_session_id}

    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.return_value = (
        mock_decoded_token
    )
    mock_finding_session_id_by_sid.return_value = mock_session_id

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)

    mock_back_channel_logout_service.oidc_service.set_up_oidc_parameters.assert_called_once()
    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.assert_called_with(
        mock_token
    )
    mock_finding_session_id_by_sid.assert_not_called()


def test_back_channel_logout_handler_no_session_id_raise_error(
    mock_back_channel_logout_service, mock_finding_session_id_by_sid
):
    mock_token = "mock_token"
    mock_session_id = "mock_session_id"
    mock_decoded_token = {"sid": mock_session_id}

    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.return_value = (
        mock_decoded_token
    )
    mock_finding_session_id_by_sid.return_value = None

    with pytest.raises(LogoutFailureException):
        mock_back_channel_logout_service.logout_handler(mock_token)

    mock_back_channel_logout_service.oidc_service.set_up_oidc_parameters.assert_called_once()
    mock_back_channel_logout_service.oidc_service.validate_and_decode_token.assert_called_with(
        mock_token
    )
    mock_finding_session_id_by_sid.assert_called_with(mock_session_id)


def test_back_channel_logout_handler_valid_jwt_no_error_raise_if_session_exists(
    mock_back_channel_logout_service,
    context,
    mock_finding_session_id_by_sid,
    mock_remove_session_from_dynamo_db,
):
    try:
        mock_token = "mock_token"
        mock_session_id = "mock_session_id"
        mock_decoded_token = {"sid": mock_session_id}

        mock_back_channel_logout_service.oidc_service.validate_and_decode_token.return_value = (
            mock_decoded_token
        )
        mock_finding_session_id_by_sid.return_value = mock_session_id

        mock_back_channel_logout_service.logout_handler(mock_token)

        mock_back_channel_logout_service.oidc_service.set_up_oidc_parameters.assert_called_once()
        mock_back_channel_logout_service.oidc_service.validate_and_decode_token.assert_called_with(
            mock_token
        )
        mock_finding_session_id_by_sid.assert_called_with(mock_session_id)
    except LogoutFailureException as e:
        assert False, e
