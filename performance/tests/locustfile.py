import os
from locust import HttpUser, task, between
from locust.user.task import TaskSetMeta
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import csv

from actions import (
    login,
    search_patient,
    stitch_view_document,
    logout,
    create_upload_intent,
)

import logging

logger = logging.getLogger(__name__)
load_dotenv()

counter_variable = 0


def load_csv_to_dict_array(file_path):
    dict_array = []
    with open(file_path, mode="r", newline="") as csvfile:
        csvreader = csv.DictReader(csvfile)
        dict_array.extend(csvreader)
    return dict_array


data = load_csv_to_dict_array("./data/users/users.csv")


class TestFramework(HttpUser):
    wait_time = between(7, 10)

    def on_start(self):
        global counter_variable
        counter_variable += 1

    @task
    def open_fullscreen_view(self):
        # test_number = (counter_variable % 5) + 1
        # logger.info("Initiating Test as - " + str(test_number))
        try:
            user_info = data[(counter_variable % 2) - 1]
            logger.info(
                f"Username: {user_info['Username']}, Password: {user_info['Password']}"
            )
            auth_headers = login.authenticate_user(self, user_info)
            if auth_headers:
                patient_id = os.getenv("PATIENT_ID")
                lgs = search_patient.search_patient(self, auth_headers, patient_id)
                logger.info(f"Attempting to load search patient result: {lgs}")

                stitch_view_document.retrieve_presigned_document(self.client, lgs)

                logout.logout(self.client, auth_headers)

        except Exception:
            logger.exception("Exception occurred", exc_info=True)

    # @task
    # def upload_files(self):
    #     try:
    #         auth_headers = login.authenticate_user(self)
    #         patient_id = "9730787212"  # Patient ID should be determined as needed
    #         logger.warn(f"Patient ID set to: {patient_id}")
    #         search_patient.search_patient(self, auth_headers, patient_id, False)
    #
    #         directory_path = f"./data/{patient_id}"  # Replace with your directory path
    #         file_objects = [
    #             {"full_path": os.path.join(directory_path, f), "filename": f}
    #             for f in os.listdir(directory_path)
    #             if os.path.isfile(os.path.join(directory_path, f))
    #         ]
    #
    #         create_upload_intent.start_upload(
    #             self,
    #             {
    #                 "auth_headers": auth_headers,
    #                 "patientId": patient_id,
    #                 "page": file_objects,
    #             },
    #         )
    #
    #     except Exception:
    #         logger.exception("Exception occurred", exc_info=True)
