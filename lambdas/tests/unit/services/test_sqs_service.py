import json

from services.sqs_service import SQSService
from tests.unit.conftest import MOCK_LG_METADATA_SQS_QUEUE, TEST_NHS_NUMBER


def test_send_message_with_nhs_number_attr(set_env, mocker):
    mocked_sqs_client = mocker.MagicMock()

    def return_mock(service_name, **_kwargs):
        if service_name == "sqs":
            return mocked_sqs_client

    mocker.patch("boto3.client", side_effect=return_mock)

    service = SQSService()

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
        DelaySeconds=0,
        MessageGroupId="test_group_id",
    )
