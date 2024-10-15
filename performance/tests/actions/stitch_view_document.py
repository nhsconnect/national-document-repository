import os
from locust import HttpUser


def retrieve_presigned_document(client, lgs):
    env_id = os.getenv("CIS2_ENV_ID")
    client.get(
        lgs
        + f"&origin=https://{env_id}.access-request-fulfilment.patient-deductions.nhs.uk/patient/lloyd-george-record#toolbar=0",
        name="Download Stitched PDF ",
    )
