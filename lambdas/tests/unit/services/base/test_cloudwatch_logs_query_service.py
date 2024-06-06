import pytest
from models.cloudwatch_logs_query import CloudwatchLogsQueryParams
from services.base.cloudwatch_logs_query_service import CloudwatchLogsQueryService
from tests.unit.conftest import WORKSPACE
from tests.unit.data.statistic.mock_logs_query_results import (
    EXPECTED_QUERY_RESULT,
    MOCK_RESPONSE_QUERY_COMPLETE,
    MOCK_RESPONSE_QUERY_FAILED,
    MOCK_RESPONSE_QUERY_IN_PROGRESS,
)
from utils.exceptions import LogsQueryException

MOCK_QUERY_ID = "mock_query_id"
MOCK_LAMBDA_NAME = "mock-lambda"
MOCK_QUERY_STRING = """
        fields @timestamp, Message, Authorisation.selected_organisation.org_ods_code AS ods_code 
        | filter Message = 'User has viewed Lloyd George records' 
        | stats count() AS daily_count_viewed BY ods_code
    """
MOCK_QUERY_PARAMS = CloudwatchLogsQueryParams(MOCK_LAMBDA_NAME, MOCK_QUERY_STRING)
MOCK_START_TIME = 1717667304
MOCK_END_TIME = 171777304


@pytest.fixture
def mock_service(set_env, mock_logs_client, patch_sleep):
    service = CloudwatchLogsQueryService()
    yield service


@pytest.fixture
def patch_sleep(mocker):
    mocker.patch("time.sleep")


@pytest.fixture
def mock_logs_client(mocker):
    mock_instance = mocker.patch("boto3.client").return_value
    yield mock_instance


def test_query_logs(mock_logs_client, mock_service):
    mock_logs_client.start_query.return_value = {"queryId": MOCK_QUERY_ID}
    mock_logs_client.get_query_results.side_effect = [
        MOCK_RESPONSE_QUERY_IN_PROGRESS,
        MOCK_RESPONSE_QUERY_IN_PROGRESS,
        MOCK_RESPONSE_QUERY_COMPLETE,
    ]
    expected = EXPECTED_QUERY_RESULT
    expected_start_query_call = {
        "logGroupName": f"/aws/lambda/{WORKSPACE}_{MOCK_QUERY_PARAMS.lambda_name}",
        "startTime": MOCK_START_TIME,
        "endTime": MOCK_END_TIME,
        "queryString": MOCK_QUERY_PARAMS.query_string,
    }

    actual = mock_service.query_logs(
        query_params=MOCK_QUERY_PARAMS,
        start_time=MOCK_START_TIME,
        end_time=MOCK_END_TIME,
    )

    assert actual == expected

    mock_logs_client.start_query.assert_called_with(**expected_start_query_call)
    mock_logs_client.get_query_results.assert_called_with(queryId=MOCK_QUERY_ID)


def test_poll_query_result_poll_result_until_complete(mock_logs_client, mock_service):
    mock_logs_client.get_query_results.side_effect = [
        MOCK_RESPONSE_QUERY_IN_PROGRESS,
        MOCK_RESPONSE_QUERY_IN_PROGRESS,
        MOCK_RESPONSE_QUERY_COMPLETE,
    ]

    actual = mock_service.poll_query_result(MOCK_QUERY_ID)
    expected = MOCK_RESPONSE_QUERY_COMPLETE["results"]

    assert actual == expected

    mock_logs_client.get_query_results.assert_called_with(queryId=MOCK_QUERY_ID)
    assert mock_logs_client.get_query_results.call_count == 3


def test_poll_query_result_raise_error_when_exceed_max_retries(
    mock_logs_client, mock_service
):
    mock_logs_client.get_query_results.return_value = MOCK_RESPONSE_QUERY_IN_PROGRESS

    with pytest.raises(LogsQueryException):
        mock_service.poll_query_result(query_id=MOCK_QUERY_ID, max_retries=20)
    assert mock_logs_client.get_query_results.call_count == 20


def test_poll_query_result_raise_error_when_query_failed(
    mock_logs_client, mock_service
):
    mock_logs_client.get_query_results.side_effect = [
        MOCK_RESPONSE_QUERY_IN_PROGRESS,
        MOCK_RESPONSE_QUERY_IN_PROGRESS,
        MOCK_RESPONSE_QUERY_FAILED,
    ]

    with pytest.raises(LogsQueryException):
        mock_service.poll_query_result(MOCK_QUERY_ID)
    assert mock_logs_client.get_query_results.call_count == 3


def test_regroup_raw_query_result(mock_service):
    raw_query_result = [
        [
            {"field": "ods_code", "value": "Y12345"},
            {"field": "daily_count_viewed", "value": "20"},
        ],
        [
            {"field": "ods_code", "value": "H81109"},
            {"field": "daily_count_viewed", "value": "40"},
        ],
    ]
    expected = [
        {
            "ods_code": "Y12345",
            "daily_count_viewed": "20",
        },
        {
            "ods_code": "H81109",
            "daily_count_viewed": "40",
        },
    ]

    actual = mock_service.regroup_raw_query_result(raw_query_result)

    assert actual == expected
