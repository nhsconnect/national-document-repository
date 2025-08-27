import base64
import csv
import logging
import os
import random

from locust import HttpUser, TaskSet, between, task
from tests.e2e.api.test_upload_document_api import create_upload_payload
from tests.e2e.conftest import API_KEY, LLOYD_GEORGE_SNOMED, generate_nhs_number


def random_item_in_csv(data):
    random_index = random.randint(0, len(data) - 1)
    return data[random_index]


def get_id(data_list, size):
    ids = []
    for data in data_list:
        if "size" in data and "id" in data:
            if data["size"] == size:
                logging.debug(f"Matching data found: {data}")
                ids.append(data["id"])
    return random.choice(ids) if ids else None


def load_csv_data(file_name):
    file_path = os.path.join(os.path.dirname(__file__), "data", file_name)
    with open(file_path, mode="r") as file:
        return list(csv.DictReader(file))


retrieve_data = load_csv_data("retrieve_data.csv")
# id, file_selection
search_data = load_csv_data("search_data.csv")
# nhs_number


class UserBehavior(TaskSet):
    def retrieve(self, use_presign, size):
        id = get_id(retrieve_data, size)
        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
        response = self.client.get(
            f"/FhirDocumentReference/{LLOYD_GEORGE_SNOMED}~{id}",
            headers=headers,
            name=f"Retrieve Document Metadata - {size}",
        )
        logging.info(response)
        if use_presign:
            try:
                response_data = response.json()
                presign_url = response_data["content"][0]["attachment"]["url"]
                self.client.get(
                    presign_url,
                    name="Retrieve Document Presign URL Invocation - " + size,
                )
            except ValueError:
                logging.error("Failed to parse JSON response", exc_info=True)

    def upload(self, use_presign, size):
        lloyd_george_record = {}
        lloyd_george_record["ods"] = "H81109"
        lloyd_george_record["nhs_number"] = generate_nhs_number()
        sample_pdf_path = os.path.join(os.path.dirname(__file__), "data/files", size)
        if not use_presign:
            with open(sample_pdf_path, "rb") as f:
                lloyd_george_record["data"] = base64.b64encode(f.read()).decode("utf-8")
        payload = create_upload_payload(lloyd_george_record)
        logging.info(payload)

        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}

        url = "/FhirDocumentReference"
        response = self.client.post(
            url, headers=headers, name=f"Post Document Reference {size}", data=payload
        )
        logging.info(response.json())
        if use_presign:
            sample_pdf_path = os.path.join(
                os.path.dirname(__file__), "data/files", size
            )
            response_data = response.json()
            presign_url = response_data["content"][0]["attachment"]["url"]

            with open(sample_pdf_path, "rb") as f:
                files = {"file": f}
                response = self.client.put(
                    presign_url,
                    name=f"Upload file of size {size} presign_url",
                    files=files,
                )

    @task(1)
    def search_document_references(self):
        search_info = random_item_in_csv(search_data)
        headers = {"Authorization": "Bearer 123", "X-Api-Key": API_KEY}
        response = self.client.get(
            f"/FhirDocumentReference?subject:identifier=https://fhir.nhs.uk/Id/nhs-number|{search_info['nhs_number']}",
            headers=headers,
            name="Search Document References",
        )
        logging.info(response.json())

    @task(1)
    def post_60kb(self):
        self.upload(False, "60kb.pdf")

    @task(1)
    def post_10mb(self):
        self.upload(True, "10mb.pdf")

    @task(1)
    def post_90mb(self):
        self.upload(True, "90mb.pdf")

    @task(1)
    def retrieve_60kb(self):
        self.retrieve(False, "60kb.pdf")

    @task(1)
    def retrieve_10mb(self):
        self.retrieve(True, "10mb.pdf")

    @task(1)
    def retrieve_90mb(self):
        self.retrieve(True, "90mb.pdf")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
