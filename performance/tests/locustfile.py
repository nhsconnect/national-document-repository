from locust import HttpUser, task
from locust.user.task import TaskSetMeta
from cis2_auth.cis2_auth import authenticate
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)
load_dotenv()


class TestFramework(HttpUser):
    @task
    def login_test(self):
        response = self.client.get(
            "/dev/Auth/Login", allow_redirects=False, name="Initiate CIS2"
        )
        location_header = response.headers.get("Location")
        if location_header:
            logger.info(f"Location header: {location_header}")
            parsed_url = urlparse(location_header)
            state = parse_qs(parsed_url.query).get("state", [None])[0]
            logger.info(state)
            try:
                code = authenticate(state)
                params = {"code": code, "state": state}
                response = self.client.get(
                    "/dev/Auth/TokenRequest",
                    params=params,
                    name="Get CIS2 Token",
                )
                auth_headers = {
                    "Authorization": response.json().get("authorisation_token")
                }
                logger.info(auth_headers)
                searchPatient = {"patientId": "9730787506"}

                self.client.get(
                    "/dev/SearchPatient",
                    headers=auth_headers,
                    params=searchPatient,
                    name="Search for a Patient",
                )
                response = self.client.get(
                    "/dev/LloydGeorgeStitch",
                    headers=auth_headers,
                    params=searchPatient,
                    name="Retrieve Presigned URL for LGS",
                )
                lgs = response.json().get("presign_url")
                logger.info(lgs)

                self.client.get(
                    lgs
                    + "&origin=https://ndr-dev.access-request-fulfilment.patient-deductions.nhs.uk/patient/lloyd-george-record#toolbar=0",
                    name="Download PDF Content",
                )
                self.client.get("/dev/Auth/Logout", headers=auth_headers, name="Logout")

            except Exception:
                logger.exception("Exception occurred", exc_info=True)
