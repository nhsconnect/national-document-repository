import io
import logging
import os
import uuid

import requests
from tests.e2e.helpers.lloyd_george_data_helper import LloydGeorgeDataHelper

data_helper = LloydGeorgeDataHelper()

api_endpoint = os.environ.get("NDR_API_ENDPOINT")
api_key = os.environ.get("NDR_API_KEY")
dynamo_table = os.environ.get("NDR_DYNAMO_STORE") or ""


def test_search_patient_details(test_data, snapshot):
    lloyd_george_record = {}
    test_data.append(lloyd_george_record)

    lloyd_george_record["id"] = str(uuid.uuid4())
    lloyd_george_record["nhs_number"] = "9449305943"
    lloyd_george_record["data"] = io.BytesIO(b"Sample PDF Content")

    data_helper.create_metadata(lloyd_george_record)
    data_helper.create_resource(lloyd_george_record)

    url = f"https://{api_endpoint}/FhirDocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{lloyd_george_record['nhs_number']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-ID": "1234",
    }
    response = requests.request("GET", url, headers=headers)
    bundle = response.json()
    logging.info(bundle)

    del bundle["entry"][0]["resource"]["id"]
    del bundle["entry"][0]["resource"]["date"]
    del bundle["timestamp"]
    attachment_url = bundle["entry"][0]["resource"]["content"][0]["attachment"]["url"]
    assert (
        "https://internal-dev.api.service.nhs.uk/national-document-repository/DocumentReference/16521000000101~"
        in attachment_url
    )
    del bundle["entry"][0]["resource"]["content"][0]["attachment"]["url"]

    assert bundle["entry"][0] == snapshot


def test_multiple_cancelled_search_patient_details(test_data, snapshot):
    lloyd_george_record = {}
    test_data.append(lloyd_george_record)

    lloyd_george_record["id"] = str(uuid.uuid4())
    lloyd_george_record["nhs_number"] = "9449305943"
    lloyd_george_record["data"] = io.BytesIO(b"Sample PDF Content")
    lloyd_george_record["doc_status"] = "cancelled"

    data_helper.create_metadata(lloyd_george_record)
    data_helper.create_resource(lloyd_george_record)

    second_lloyd_george_record = {}
    test_data.append(second_lloyd_george_record)

    second_lloyd_george_record["id"] = str(uuid.uuid4())
    second_lloyd_george_record["nhs_number"] = "9449305943"
    second_lloyd_george_record["data"] = io.BytesIO(b"Sample PDF Content")
    second_lloyd_george_record["doc_status"] = "cancelled"

    data_helper.create_metadata(second_lloyd_george_record)
    data_helper.create_resource(second_lloyd_george_record)

    url = f"https://{api_endpoint}/FhirDocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{lloyd_george_record['nhs_number']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-ID": "1234",
    }
    response = requests.request("GET", url, headers=headers)
    bundle = response.json()

    del bundle["timestamp"]
    del bundle["entry"][0]["resource"]["id"]
    del bundle["entry"][0]["resource"]["date"]
    del bundle["entry"][0]["resource"]["content"][0]["attachment"]["url"]
    del bundle["entry"][1]["resource"]["id"]
    del bundle["entry"][1]["resource"]["date"]
    del bundle["entry"][1]["resource"]["content"][0]["attachment"]["url"]

    assert bundle["entry"][0] == snapshot
    assert bundle["entry"][1] == snapshot


def test_no_records(snapshot):
    lloyd_george_record = {}  # Initialize the dictionary
    lloyd_george_record["nhs_number"] = "9449305943"

    url = f"https://{api_endpoint}/FhirDocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{lloyd_george_record['nhs_number']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-ID": "1234",
    }
    response = requests.request("GET", url, headers=headers)
    bundle = response.json()

    assert bundle == snapshot


def test_invalid_patient(snapshot):
    lloyd_george_record = {}
    lloyd_george_record["nhs_number"] = "9999999993"

    url = f"https://{api_endpoint}/FhirDocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{lloyd_george_record['nhs_number']}"
    headers = {
        "Authorization": "Bearer 123",
        "X-Api-Key": api_key,
        "X-Correlation-ID": "1234",
    }
    response = requests.request("GET", url, headers=headers)
    bundle = response.json()

    assert bundle == snapshot
