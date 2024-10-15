from locust import HttpUser
import logging

logger = logging.getLogger(__name__)


def search_patient(client: HttpUser, auth_headers, patient_id, expect_to_be_found=True):
    search_patient_params = {"patientId": patient_id}
    logger.info(search_patient_params)
    client.client.get(
        "/SearchPatient",
        headers=auth_headers,
        params=search_patient_params,
        name="Search for a Patient",
    )

    with client.client.get(
        "/LloydGeorgeStitch",
        headers=auth_headers,
        params=search_patient_params,
        name="Stitch Documents",
        catch_response=True,
    ) as response:
        if response.status_code == 404 and not expect_to_be_found:
            logger.info(
                "LloydGeorgeStitch returned 404: Not Found, However this was expected"
            )
            response.success()
            return None
        return response.json().get("presign_url")
