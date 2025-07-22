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


def test_search_patient_details(cleanup_dynamo):
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

    # Check that a bundle of documents is returned (Patient may have multiple)
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "searchset"
    assert bundle["total"] == 1
    assert "entry" in bundle and len(bundle["entry"]) > 0

    # Check the first resource, our controlled test should only have one
    doc = bundle["entry"][0]["resource"]

    # Check document metadata
    assert doc["resourceType"] == "DocumentReference"
    assert doc["status"] == "current"
    assert doc["docStatus"] == "final"

    # Check coding
    coding = doc["type"]["coding"][0]
    assert coding["code"] == "16521000000101"
    assert coding["display"] == "Lloyd George record folder"

    # Check patient NHS number
    subject_id = doc["subject"]["identifier"]
    assert subject_id["system"] == "https://fhir.nhs.uk/Id/nhs-number"
    assert subject_id["value"] == "9449305943"

    # Check author and custodian
    author_id = doc["author"][0]["identifier"]
    custodian_id = doc["custodian"]["identifier"]
    assert author_id["value"] == "H81109"
    assert custodian_id["value"] == "H81109"

    # Check content metadata
    attachment = doc["content"][0]["attachment"]
    assert attachment["contentType"] == "application/pdf"
    assert attachment["language"] == "en-GB"
    assert (
        attachment["title"]
        == f"1of1_Lloyd_George_Record_[Holly Lorna MAGAN]_[{nhs_number}]_[29-05-2006].pdf"
    )
    assert (
        attachment["url"]
        == f"https://internal-dev.api.service.nhs.uk/national-document-repository/DocumentReference/16521000000101~{random_guid}"
    )
    assert attachment["creation"] == "2023-01-01"
