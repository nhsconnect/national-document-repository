import base64
import csv
import logging
import os
import random

from locust import HttpUser, TaskSet, between, task
from tests.e2e.api.test_upload_document_api import create_upload_payload
from tests.e2e.conftest import API_KEY, LLOYD_GEORGE_SNOMED


def random_item_in_csv(data):
    random_index = random.randint(0, len(data) - 1)
    return data[random_index]


def load_csv_data(file_name):
    file_path = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(file_path, mode="r") as file:
        return list(csv.DictReader(file))


retrieve_presign_data = load_csv_data("retrieve_data_presign.csv")
retrieve_base64_data = load_csv_data("retrieve_data_base64.csv")
search_data = load_csv_data("search_data.csv")
upload_data = load_csv_data("upload_data.csv")


class UserBehavior(TaskSet):
    @task(1)
    def retrieve_presign(self):
        retrieve_info = random_item_in_csv(retrieve_presign_data)
        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
        response = self.client.get(
            f"/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{retrieve_info['id']}",
            headers=headers,
            name="Retrieve Document Metadata",
        )
        try:
            response_data = response.json()
            presign_url = response_data["content"][0]["attachment"]["url"]
            self.client.get(
                presign_url,
                name="Retrieve Document Presign URL Invocation - "
                + retrieve_info["size_category"],
            )

        except ValueError:
            logging.error("Failed to parse JSON response", exc_info=True)

    @task(2)
    def retrieve_base64(self):
        retrieve_info = random_item_in_csv(retrieve_base64_data)
        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
        response = self.client.get(
            f"/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{retrieve_info['id']}",
            headers=headers,
            name="Retrieve Document Metadata",
        )
        response.json()

    @task(3)
    def search_document_references(self):
        search_info = random_item_in_csv(search_data)
        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
        response = self.client.get(
            f"/FhirDocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{search_info['nhs_number']}",
            headers=headers,
            name="Search Document References",
        )
        logging.info(response.json())

    @task(4)
    def post_document_references(self):
        post_info = random_item_in_csv(upload_data)
        lloyd_george_record = {}
        lloyd_george_record["ods"] = post_info["ods"]
        lloyd_george_record["nhs_number"] = post_info["nhs_number"]
        sample_pdf_path = os.path.join(
            os.path.dirname(__file__), "data/files", "dummy.pdf"
        )
        with open(sample_pdf_path, "rb") as f:
            lloyd_george_record["data"] = base64.b64encode(f.read()).decode("utf-8")
        payload = create_upload_payload(lloyd_george_record)

        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}

        url = "/FhirDocumentReference"
        response = self.client.post(
            url, headers=headers, name="Post Document Reference", data=payload
        )
        logging.info(response.json())


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
