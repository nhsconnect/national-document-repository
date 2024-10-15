import requests
import html
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
    logger.info(f"Request: URL = {base_url}, Params = {params}")
    response = session.post(base_url, params=params)
    logger.info(
        f"Response: Status Code = {response.status_code}, Content = {response.text}"
    )
    if response.status_code == 200:
        return response.json().get("authId")
    else:
        logger.error("Failed to get CIS2 authentication token")
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
    url = f"{BASE_URL}/openam/json/realms/root/realms/oidc/authenticate"
    query_params = {
        "authIndexType": "service",
        "authIndexValue": "DefaultAuthTree",
        "goto": params["goto"],
    }

    logger.info(
        f"Request: URL = {url}, Headers = {'Content-Type: application/json'}, Payload = {payload}, Params = {query_params}"
    )
    response = session.request(
        "POST",
        url,
        headers={"Content-Type": "application/json"},
        data=payload,
        params=query_params,
    )

    json_output = response.json()["callbacks"][0]["output"][0]["value"]
    unescaped_output = html.unescape(json_output)
    formatted_output = json.loads(unescaped_output)

    logger.info(
        f"Response: Status Code = {response.status_code}, Content = {json.dumps(formatted_output, indent=4)}"
    )
    if response.status_code == 200:
        return response.json().get("authId")
    else:
        logger.error("Failed to get list of roles")
        return None


def assume_role(params):
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
        f"&redirect_uri=https://{os.getenv('CIS2_ENV_ID')}.access-request-fulfilment.patient-deductions.nhs.uk/auth-callback"
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

    logger.info(
        f"Request: URL = {url}, Headers = {'Content-Type: application/json'}, Payload = {payload}, Params = {query_params}"
    )
    response = session.request(
        "POST",
        url,
        headers={"Content-Type": "application/json"},
        data=payload,
        params=query_params,
    )
    logger.info(
        f"Response: Status Code = {response.status_code}, Content = {response.text}"
    )
    try:
        return response.json().get("successUrl")
    except ValueError:
        logger.error("Failed to assume role")
        return None


def intercept_redirect(url):
    logger.info(f"Intercepting redirect URL: {url}")
    response = session.get(url, allow_redirects=False)
    logger.info(
        f"Response: Status Code = {response.status_code}, Headers = {response.headers}"
    )
    for header, value in response.headers.items():
        if header == "Location":
            url = value
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            code = query_params.get("code", [None])[0]
            logger.info(f"Intercepted Code: {code}")
            return code


def authenticate(state, user):
    assert "CIS2_ACR_SIG" in os.environ, "CIS2_ACR_SIG environment variable is missing"
    assert (
        "CIS2_CLIENT_ID" in os.environ
    ), "CIS2_CLIENT_ID environment variable is missing"

    logger.info(f"Authentication State: {state}")
    params = {
        "authIndexType": "service",
        "authIndexValue": "DefaultAuthTree",
        "state": state,
    }
    authentication_response = get_cis2_authentication_token(params)
    if authentication_response:
        logger.info(
            f"Successfully authenticated with authId: {authentication_response}"
        )
    else:
        logger.error("Authentication failed")
    goto_url = (
        f"{BASE_URL}:443/openam/oauth2"
        "/realms/root/realms/oidc/authorize?"
        "response_type=code"
        f"&client_id={os.getenv('CIS2_CLIENT_ID')}"
        f"&redirect_uri=https://{os.getenv('CIS2_ENV_ID')}.access-request-fulfilment.patient-deductions.nhs.uk/auth-callback&"
        "scope=openid%20profile%20nhsperson%20nationalrbacaccess%20selectedrole&"
        f"state={state}&prompt=&acr=AAL1_USERPASS&"
        f"acr_sig={os.getenv('CIS2_ACR_SIG')}"
    )
    roles_params = {
        "authId": authentication_response,
        "username": user["Username"],
        "password": user["Password"],
        "goto": goto_url,
    }

    roles_response = get_list_of_roles(roles_params)
    assume_roles_params = {
        "authId": roles_response,
        "assumedRole": user["AssumedRole"],
        "state": state,
    }
    role_assumption_response = assume_role(assume_roles_params)
    return intercept_redirect(role_assumption_response)
