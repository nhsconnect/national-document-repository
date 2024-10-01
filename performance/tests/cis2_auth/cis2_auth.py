import requests
import logging
import json
from urllib.parse import urlparse, parse_qs
import os

BASE_URL = os.getenv(
    "CIS_BASE_URL", "https://am.nhsdev.auth-ptl.cis2.spineservices.nhs.uk"
)
logger = logging.getLogger(__name__)
session = requests.Session()


# region CIS2 Authentication Token
def get_cis2_authentication_token(params):
    session.cookies.clear()
    base_url = f"{BASE_URL}/openam/json/realms/root/realms/oidc/authenticate"
    logger.info("Getting CIS2 authentication token with params: " + str(params))
    response = session.post(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("authId")
    else:
        logger.error("Failed to get CIS2 authentication token: " + str(response))
        return None


# endregion CIS2 Authentication Token
# region CIS2 Roles Retrieval
def get_list_of_roles(params):
    payload = json.dumps(
        {
            "authId": params["authId"],
            "callbacks": [
                {
                    "type": "NameCallback",
                    "output": [{"name": "prompt", "value": "User Name"}],
                    "input": [{"name": "IDToken1", "value": params["username"]}],
                    "_id": 0,
                },
                {
                    "type": "PasswordCallback",
                    "output": [{"name": "prompt", "value": "Password"}],
                    "input": [
                        {
                            "name": "IDToken2",
                            "value": params["password"],
                        }
                    ],
                    "_id": 1,
                },
            ],
            "status": 200,
            "ok": True,
        }
    )
    logging.info("Getting list of roles with payload: " + payload)
    url = f"{BASE_URL}/openam/json/realms/root/realms/oidc/authenticate"
    query_params = {
        "authIndexType": "service",
        "authIndexValue": "DefaultAuthTree",
        "goto": params["goto"],
    }

    headers = {
        "Content-Type": "application/json",
    }
    response = session.request(
        "POST", url, headers=headers, data=payload, params=query_params
    )
    if response.status_code == 200:
        logger.info(response.json())
        return response.json().get("authId")
    else:
        logger.error("Failed to get CIS2 authentication token: " + response.text)
        return None


def assume_role(params):
    logger.info("Assuming role with params: " + str(params))
    payload = json.dumps(
        {
            "authId": params["authId"],
            "callbacks": [
                {
                    "type": "HiddenValueCallback",
                    "output": [
                        {"name": "value", "value": ""},
                        {"name": "id", "value": "nhsRoles"},
                    ],
                    "input": [{"name": "IDToken1", "value": "nhsRoles"}],
                },
                {
                    "type": "HiddenValueCallback",
                    "output": [
                        {"name": "value", "value": ""},
                        {"name": "id", "value": "selectedRole"},
                    ],
                    "input": [{"name": "IDToken2", "value": params["assumedRole"]}],
                },
            ],
            "stage": "roleSelection",
            "status": 200,
            "ok": True,
        }
    )
    url = f"{BASE_URL}/openam/json/realms/root/realms/oidc/authenticate"
    goto = (
        f"{BASE_URL}:443/openam/oauth2/realms/root/realms/oidc/authorize"
        "?response_type=code"
        f"&client_id={os.getenv('CIS2_CLIENT_ID')}"
        "&redirect_uri=https://ndr-dev.access-request-fulfilment.patient-deductions.nhs.uk/auth-callback"
        "&scope=openid%20profile%20nhsperson%20nationalrbacaccess%20selectedrole"
        f"&state={params['state']}"
        "&prompt="
        "&acr=AAL1_USERPASS"
        f"acr_sig={os.getenv('CIS2_ACR_SIG')}"
    )
    query_params = {
        "authIndexType": "service",
        "authIndexValue": "DefaultAuthTree",
        "goto": goto,
    }
    headers = {"Content-Type": "application/json"}
    response = session.request(
        "POST", url, headers=headers, data=payload, params=query_params
    )
    try:
        logger.info(response.json())
    except ValueError:
        logger.error(response.text)
    return response.json().get("successUrl")


def intercept_redirect(url):
    logger.info(url)
    response = session.get(url, allow_redirects=False)
    for header, value in response.headers.items():
        if header == "Location":
            url = value
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            code = query_params.get("code", [None])[0]
            logger.info(f"Code: {code}")
            return code


def authenticate(state):
    assert (
        "CIS2_AUTH_PASSWORD" in os.environ
    ), "CIS2_AUTH_PASSWORD environment variable is missing"
    assert "CIS2_ACR_SIG" in os.environ, "CIS2_ACR_SIG environment variable is missing"
    assert (
        "CIS2_CLIENT_ID" in os.environ
    ), "CIS2_CLIENT_ID environment variable is missing"

    logger.info(state)
    params = {
        "authIndexType": "service",
        "authIndexValue": "DefaultAuthTree",
        "state": state,
    }
    authentication_response = get_cis2_authentication_token(params)
    if authentication_response:
        logger.info(
            "Successfully authenticated with authId: " + authentication_response
        )
    else:
        logger.error("Authentication failed")
    goto_url = (
        f"{BASE_URL}:443/openam/oauth2"
        "/realms/root/realms/oidc/authorize?"
        "response_type=code"
        f"&client_id={os.getenv('CIS2_CLIENT_ID')}"
        "&redirect_uri=https://ndr-dev.access-request-fulfilment.patient-deductions.nhs.uk/auth-callback&"
        "scope=openid%20profile%20nhsperson%20nationalrbacaccess%20selectedrole&"
        f"state={state}&prompt=&acr=AAL1_USERPASS&"
        f"acr_sig={os.getenv('CIS2_ACR_SIG')}"
    )
    roles_params = {
        "authId": authentication_response,
        "username": "555053895106",
        "password": os.getenv("CIS2_AUTH_PASSWORD"),
        "goto": goto_url,
    }

    ## Stage 2: Get a list of all avaialable roles to impersonate as
    roles_response = get_list_of_roles(roles_params)
    ## Stage 3: Assume a role
    assume_roles_params = {
        "authId": roles_response,
        "assumedRole": "555056245106",
        "state": state,
    }
    role_assumption_response = assume_role(assume_roles_params)
    intercept_redirect_code = intercept_redirect(role_assumption_response)
    return intercept_redirect_code
