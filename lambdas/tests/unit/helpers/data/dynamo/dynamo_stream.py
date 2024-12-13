from models.document_reference import DocumentReference
from tests.unit.conftest import (
    TEST_CURRENT_GP_ODS,
    TEST_DOCUMENT_LOCATION,
    TEST_FILE_KEY,
    TEST_NHS_NUMBER,
    TEST_UUID,
)
from utils.dynamo_utils import parse_dynamo_record

MOCK_DYNAMO_STREAM_EVENT = {
    "Records": [
        {
            "eventID": "36ddd0fac61a24a164c69ee01a145e65",
            "eventName": "REMOVE",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "eu-west-2",
            "dynamodb": {
                "ApproximateCreationDateTime": 1733485731.0,
                "Keys": {"ID": {"S": f"{TEST_UUID}"}},
                "OldImage": {
                    "ContentType": {"S": "application/pdf"},
                    "FileName": {"S": f"{TEST_FILE_KEY}"},
                    "Uploading": {"BOOL": False},
                    "TTL": {"N": "1738238333"},
                    "Created": {"S": "2024-11-27T16:30:11.532530Z"},
                    "Uploaded": {"BOOL": True},
                    "FileLocation": {"S": f"{TEST_DOCUMENT_LOCATION}"},
                    "CurrentGpOds": {"S": f"{TEST_CURRENT_GP_ODS}"},
                    "VirusScannerResult": {"S": "Clean"},
                    "Deleted": {"S": "2024-12-05T11:58:53.527237Z"},
                    "ID": {"S": f"{TEST_UUID}"},
                    "LastUpdated": {"N": "1732725252"},
                    "NhsNumber": {"S": f"{TEST_NHS_NUMBER}"},
                },
                "SequenceNumber": "1044384700000000014787528151",
                "SizeBytes": 474,
                "StreamViewType": "OLD_IMAGE",
            },
            "eventSourceARN": "arn:aws:dynamodb:eu-west-2:5000000000:table/dynamo-table/stream/2024-12-06T12:00:00.000",
        }
    ]
}

MOCK_OLD_IMAGE_EVENT = MOCK_DYNAMO_STREAM_EVENT["Records"][0]["dynamodb"]["OldImage"]

MOCK_OLD_IMAGE_MODEL = DocumentReference.model_validate(
    parse_dynamo_record(MOCK_OLD_IMAGE_EVENT)
)
