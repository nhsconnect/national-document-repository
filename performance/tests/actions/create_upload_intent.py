from locust import HttpUser
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def start_upload(user: HttpUser, documentRequestDetails):
    pages = documentRequestDetails["page"]
    document_reference = {
        "resourceType": "DocumentReference",
        "subject": {
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/nhs-number",
                "value": documentRequestDetails["patientId"],
            }
        },
        "type": {
            "coding": [{"system": "http://snomed.info/sct", "code": "22151000087106"}]
        },
        "content": [{"attachment": [convert_page_object(page) for page in pages]}],
        "created": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
    }
    logger.warn(document_reference)
    response = user.client.post(
        "/DocumentReference",
        json=document_reference,
        headers=documentRequestDetails["auth_headers"],
        name="Get the template for uploading the documents",
    )

    logger.info(response.json())


def convert_page_object(page):
    return {
        "fileName": page["filename"],
        "contentType": "application/pdf",
        "docType": "LG",
        "clientId": str(uuid.uuid4()),
    }
