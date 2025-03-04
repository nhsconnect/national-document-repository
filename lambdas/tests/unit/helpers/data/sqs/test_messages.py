from unit.conftest import TEST_NHS_NUMBER, TEST_UUID

stitching_queue_message_event = {
    "Records": [
        {
            "messageId": TEST_UUID,
            "receiptHandle": "1234",
            "body": {
                "nhs_number": TEST_NHS_NUMBER,
                "snomed_code_doc_type": {
                    "code": "16521000000101",
                    "display_name": "Lloyd George record folder",
                },
            },
            "attributes": {
                "ApproximateReceiveCount": "1",
                "SentTimestamp": "1741018087746",
                "SenderId": "AAAAXYSUA44V44WUNXXXX:XXXX@hscic.gov.uk",
                "ApproximateFirstReceiveTimestamp": "1741018087747",
            },
            "messageAttributes": {},
            "md5OfBody": "2d40aef5b3e2010b57ec9ed43c48728c",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:eu-west-2:xxxx:test-stitching-queue",
            "awsRegion": "eu-west-2",
        }
    ]
}
