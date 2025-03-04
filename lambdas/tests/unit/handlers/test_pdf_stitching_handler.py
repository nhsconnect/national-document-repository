import json

from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage

test_message = (
    "{'Records': [{'messageId': '1c2eb4cc-6921-4eb6-a01a-2f5eb7fa4362', "
    "'receiptHandle': '1234', "
    "'body': '"
    "{"
    '"nhs_number":"9000000000",'
    '"snomed_code_doc_type":{"code":"16521000000101","display_name":"Lloyd George record folder"}}\', '
    "'attributes': "
    "{"
    "'ApproximateReceiveCount': '1', "
    "'SentTimestamp': '1741018087746', "
    "'SenderId': 'AAAAXYSUA44V44WUNXXXX:XXXX@hscic.gov.uk', "
    "'ApproximateFirstReceiveTimestamp': '1741018087747'"
    "}, "
    "'messageAttributes': {}, "
    "'md5OfBody': '2d40aef5b3e2010b57ec9ed43c48728c', "
    "'eventSource': 'aws:sqs', "
    "'eventSourceARN': 'arn:aws:sqs:eu-west-2:xxxx:test-stitching-queue', "
    "'awsRegion': 'eu-west-2'"
    "}"
    "]}"
)


def test_handler_parses_sqs_message():
    body = (
        '{"nhs_number": "9730787506", "snomed_code_doc_type": '
        '{"code": "16521000000101", "display_name": "Lloyd George record folder"}}'
    )
    message_body = json.loads(body)
    stitching_message = PdfStitchingSqsMessage.model_validate(message_body)

    print(stitching_message)
