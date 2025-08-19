import io
import uuid

import requests
from tests.e2e.conftest import (
    API_ENDPOINT,
    API_KEY,
    LLOYD_GEORGE_S3_BUCKET,
    LLOYD_GEORGE_SNOMED,
)
from tests.e2e.helpers.lloyd_george_data_helper import LloydGeorgeDataHelper

data_helper = LloydGeorgeDataHelper()


def test_small_file(test_data, snapshot):
    lloyd_george_record = {}
    test_data.append(lloyd_george_record)

    lloyd_george_record["id"] = str(uuid.uuid4())
    lloyd_george_record["nhs_number"] = "9449305943"
    lloyd_george_record["data"] = io.BytesIO(b"Sample PDF Content")

    data_helper.create_metadata(lloyd_george_record)
    data_helper.create_resource(lloyd_george_record)


    url = f"https://{api_endpoint}/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{lloyd_george_record['id']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-Id": "1234",
    }
    response = requests.request("GET", url, headers=headers)
    json = response.json()

    del json["date"]
    del json["id"]

    assert json == snapshot


def test_large_file(test_data, snapshot):
    lloyd_george_record = {}
    test_data.append(lloyd_george_record)

    lloyd_george_record["id"] = str(uuid.uuid4())
    lloyd_george_record["nhs_number"] = "9449305943"
    lloyd_george_record["data"] = io.BytesIO(b"A" * (10 * 1024 * 1024))
    lloyd_george_record["size"] = 10 * 1024 * 1024 * 1024

    data_helper.create_metadata(lloyd_george_record)
    data_helper.create_resource(lloyd_george_record)

    url = f"https://{api_endpoint}/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{lloyd_george_record['id']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-Id": "1234",
    
    response = requests.request("GET", url, headers=headers)
    json = response.json()

    expected_presign_uri = f"https://{LLOYD_GEORGE_S3_BUCKET}.s3.eu-west-2.amazonaws.com/{lloyd_george_record['nhs_number']}/{lloyd_george_record['id']}"
    assert expected_presign_uri in json["content"][0]["attachment"]["url"]

    del json["date"]
    del json["id"]
    del json["content"][0]["attachment"]["url"]

    assert json == snapshot


def test_no_file_found(snapshot):
    lloyd_george_record = {}
    lloyd_george_record["id"] = str(uuid.uuid4())
      
    url = f"https://{api_endpoint}/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{lloyd_george_record['id']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-Id": "1234",
    }
    response = requests.request("GET", url, headers=headers)
    json = response.json()

    assert json == snapshot


def test_preliminary_file(test_data, snapshot):
    lloyd_george_record = {}
    test_data.append(lloyd_george_record)

    lloyd_george_record["id"] = str(uuid.uuid4())
    lloyd_george_record["nhs_number"] = "9449305943"
    lloyd_george_record["data"] = io.BytesIO(b"Sample PDF Content")
    lloyd_george_record["doc_status"] = "preliminary"

    data_helper.create_metadata(lloyd_george_record)
    data_helper.create_resource(lloyd_george_record)
     
    url = f"https://{api_endpoint}/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{lloyd_george_record['id']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-Id": "1234",
    }
      
    response = requests.request("GET", url, headers=headers)
    json = response.json()

    del json["date"]
    del json["id"]

    assert json == snapshot
