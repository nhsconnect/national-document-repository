import json
import os
import requests

from tests.e2e.helpers.lloyd_george_data_helper import LloydGeorgeDataHelper
from tests.e2e.conftest import LLOYD_GEORGE_SNOMED, API_KEY, API_ENDPOINT, fetch_with_retry


data_helper = LloydGeorgeDataHelper()


def create_upload_payload(lloyd_george_record):
    sample_payload = {
        "resourceType": "DocumentReference",
        "type": {
            "coding": [
                {"system": "http://snomed.info/sct", "code": f"{LLOYD_GEORGE_SNOMED}", "display": "Lloyd George record folder"}
            ]
        },
        "subject": {"identifier": {"system": "https://fhir.nhs.uk/Id/nhs-number", "value": lloyd_george_record["nhs_number"]}},
        "author": [
            {"identifier": {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": lloyd_george_record["ods"]}}
        ],
        "custodian": {
            "identifier": {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": lloyd_george_record["ods"]}
        },
        "content": [
            {
                "attachment": {
                    "creation": "2023-01-01",
                    "contentType": "application/pdf",
                    "language": "en-GB",
                    "title": "1of1_Lloyd_George_Record_[Paula Esme VESEY]_[9730153973]_[22-01-1960].pdf",
                }
            }
        ],
    }

    if "data" in lloyd_george_record:
        sample_payload["content"][0]["attachment"]["data"] = lloyd_george_record["data"]
    return json.dumps(sample_payload)


def test_create_document_base64(test_data, snapshot):
    lloyd_george_record = {}
    lloyd_george_record["ods"] = "H81109"
    lloyd_george_record["nhs_number"] = "9449303304"
    lloyd_george_record["data"] = "aa"

    payload = create_upload_payload(lloyd_george_record)
    url = f"https://{API_ENDPOINT}/FhirDocumentReference"
    headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
    response = requests.post(url, headers=headers, data=payload)
    data = response.json()

    pass


def test_create_document_presign(test_data, snapshot):
    lloyd_george_record = {}
    lloyd_george_record["ods"] = "H81109"
    lloyd_george_record["nhs_number"] = "9449303304"

    payload = create_upload_payload(lloyd_george_record)
    url = f"https://{API_ENDPOINT}/FhirDocumentReference"
    headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}

    retrieve_response = requests.post(url, headers=headers, data=payload)
    upload_response = retrieve_response.json()
    lloyd_george_record["id"] = upload_response["id"].split("~")[1]
    test_data.append(lloyd_george_record)
    presign_uri = upload_response["content"][0]["attachment"]["url"]
    del upload_response["content"][0]["attachment"]["url"]
    del upload_response["id"]
    del upload_response["date"]

    sample_pdf_path = os.path.join(os.path.dirname(__file__), "files", "dummy.pdf")
    with open(sample_pdf_path, "rb") as f:
        files = {"file": f}
        retrieve_response = requests.put(presign_uri, files=files)
        assert retrieve_response.status_code == 200

    retrieve_url = f"https://{API_ENDPOINT}/FhirDocumentReference/{upload_response['id']}"

    def condition(response_json):
        return response_json["content"][0]["attachment"].get("url", False)

    retrieve_response = fetch_with_retry(retrieve_url, condition)

    assert upload_response == snapshot
    assert retrieve_response == snapshot

    pass


def test_create_patient_not_in_pds(test_data, snapshot):
    pass


def test_create_patient_virusscan_failure(test_data, snapshot):
    pass
