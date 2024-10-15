import logging
from locust import HttpUser
from actions.cis2_auth.cis2_auth import authenticate
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


def authenticate_user(client: HttpUser, user):
    response = client.client.get(
        "/Auth/Login", allow_redirects=False, name="Initiate CIS2"
    )
    location_header = response.headers.get("Location")
    if location_header:
        logger.info(f"Location header: {location_header}")
        parsed_url = urlparse(location_header)
        state = parse_qs(parsed_url.query).get("state", [None])[0]
        logger.info(state)
        code = authenticate(state, user)
        params = {"code": code, "state": state}
        response = client.client.get(
            "/Auth/TokenRequest", params=params, name="Get CIS2 Token"
        )
        logger.info(response.json())
        return {"Authorization": response.json().get("authorisation_token")}
    return None
