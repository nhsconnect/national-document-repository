import datetime
import io
import os
import uuid

import pytest
import requests
from services.base.dynamo_service import DynamoDBService
from services.base.s3_service import S3Service

s3_service = S3Service()
dynamo_service = DynamoDBService()

api_endpoint = os.environ.get("NDR_API_ENDPOINT")
api_key = os.environ.get("NDR_API_KEY")
s3_bucket = os.environ.get("NDR_S3_BUCKET") or ""
dynamo_table = os.environ.get("NDR_DYNAMO_STORE") or ""
random_guid = str(uuid.uuid4())


@pytest.fixture
def cleanup_dynamo():
    yield
    dynamo_service.delete_item(table_name=dynamo_table, key={"ID": random_guid})


def test_search_patient_details(cleanup_dynamo, snapshot):
    nhs_number = "9449305943"

    file_content = io.BytesIO(b"Sample PDF Content")
    s3_service.upload_file_obj(
        file_obj=file_content,
        s3_bucket_name=s3_bucket,
        file_key=f"{nhs_number}/{random_guid}",
    )

    dynamo_item = {
        "ID": random_guid,
        "ContentType": "application/pdf",
        "Created": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "CurrentGpOds": "H81109",
        "Custodian": "H81109",
        "DocStatus": "final",
        "DocumentScanCreation": "2023-01-01",
        "FileLocation": f"s3://{s3_bucket}/{nhs_number}/{random_guid}",
        "FileName": f"1of1_Lloyd_George_Record_[Holly Lorna MAGAN]_[{nhs_number}]_[29-05-2006].pdf",
        "FileSize": "128670",
        "LastUpdated": 1743177202,
        "NhsNumber": nhs_number,
        "Status": "current",
        "DocumentSnomedCode": "16521000000101",
        "Uploaded": True,
        "Uploading": False,
        "Version": "1",
        "VirusScannerResult": "Clean",
    }

    dynamo_service.create_item(dynamo_table, dynamo_item)
    url = f"https://{api_endpoint}/DocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{nhs_number}"
    headers = {"Authorization": "Bearer 123", "X-Api-Key": api_key}
    response = requests.request("GET", url, headers=headers)
    bundle = response.json()

    del bundle["entry"][0]["resource"]["id"]
    del bundle["entry"][0]["resource"]["date"]
    del bundle["timestamp"]
    attachment_url = bundle["entry"][0]["resource"]["content"][0]["attachment"]["url"]
    assert (
        "https://internal-dev.api.service.nhs.uk/national-document-repository/DocumentReference/16521000000101~"
        in attachment_url
    )
    del bundle["entry"][0]["resource"]["content"][0]["attachment"]["url"]

    assert bundle == snapshot
