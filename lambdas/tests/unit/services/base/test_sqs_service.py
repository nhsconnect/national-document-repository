import json

import pytest
from services.base.sqs_service import SQSService
from tests.unit.conftest import MOCK_LG_METADATA_SQS_QUEUE, TEST_NHS_NUMBER


@pytest.fixture()
def mocked_sqs_client(mocker):
    mocked_sqs_client = mocker.MagicMock()

    def return_mock(service_name, **_kwargs):
        if service_name == "sqs":
            return mocked_sqs_client

    mocker.patch("boto3.client", side_effect=return_mock)

    return mocked_sqs_client


@pytest.fixture()
def service(mocker, mocked_sqs_client):
    service = SQSService()
    return service


def test_send_message_with_nhs_number_attr(set_env, mocked_sqs_client, service):

    test_message_body = json.dumps(
        {"NHS-NO": "1234567890", "files": ["file1.pdf", "file2.pdf"]}
    )

    service.send_message_with_nhs_number_attr_fifo(
        group_id="test_group_id",
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=test_message_body,
        nhs_number=TEST_NHS_NUMBER,
    )

    mocked_sqs_client.send_message.assert_called_with(
        QueueUrl=MOCK_LG_METADATA_SQS_QUEUE,
        MessageAttributes={
            "NhsNumber": {"DataType": "String", "StringValue": TEST_NHS_NUMBER},
        },
        MessageBody=test_message_body,
        MessageGroupId="test_group_id",
    )


def test_send_message_fifo(set_env, mocked_sqs_client, service):
    test_message_body = json.dumps(
        {"NHS-NO": "1234567890", "files": ["file1.pdf", "file2.pdf"]}
    )

    service.send_message_fifo(
        group_id="test_group_id",
        queue_url=MOCK_LG_METADATA_SQS_QUEUE,
        message_body=test_message_body,
    )

    mocked_sqs_client.send_message.assert_called_with(
        QueueUrl=MOCK_LG_METADATA_SQS_QUEUE,
        MessageBody=test_message_body,
        MessageGroupId="test_group_id",
    )


def test_send_message_batch_standard_success(
    set_env, mocked_sqs_client, service, mocker
):
    messages = ["message1", "message2", "message3"]
    uuids = ["id-1", "id-2", "id-3"]
    mocker.patch("uuid.uuid4", side_effect=uuids.copy())

    mocked_sqs_client.send_message_batch.return_value = {
        "Successful": [{"Id": "id-1"}, {"Id": "id-2"}, {"Id": "id-3"}],
        "Failed": [],
    }

    service.send_message_batch_standard(
        queue_url="fake queue url",
        messages=messages,
        delay_between_batch_messages=0,
    )

    args = mocked_sqs_client.send_message_batch.call_args[1]
    entries = args["Entries"]
    assert len(entries) == 3
    for i, entry in enumerate(entries):
        assert entry["MessageBody"] == messages[i]
        assert entry["DelaySeconds"] == 0
        assert entry["Id"] == uuids[i]
