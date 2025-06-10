import os
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from models.oidc_models import IdTokenClaimSet
from services.login_service import LoginService
from services.mock_ods_api_service import MockOdsApiService
from typing_extensions import override
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class MockLoginService(LoginService):
    def __init__(self):
        super().__init__()
        self.ods_api_service = MockOdsApiService()
        self.base_mock_api_url = "https://identity.ptl.api.platform.nhs.uk"
        self.mock_api_key = os.environ.get("MOCK_CIS2_API_KEY_SSM")

    @override
    def generate_session(
        self,
        username: str,
        password: str,
        state: str | None = None,
        auth_code: str | None = None,
    ) -> dict:
        # TODO - Fetch MOCK_CIS2_API_KEY_SSM from SSM using os var

        # TODO - Compare password to new password SSM param (for extra security)

        logger.info("Fetching mock user information")
        userinfo = self.get_mock_user_info(username)

        mock_id_token_claim_set = IdTokenClaimSet(
            sub=userinfo["sub"],  # subject claim. user's login ID at CIS2
            sid="",  # user's session ID at CIS2
            exp=0,  # TODO: Look at ndr-dev id claim set and put same value here
            # (Might match access token endpoint 'expires_in': 3600'?)
            selected_roleid=userinfo["selected_roleid"],
        )
        selected_role_id = mock_id_token_claim_set.selected_roleid
        logger.debug(f"Selected role ID: {selected_role_id}")

        logger.info("Extracting user's organisation and smartcard codes")
        self.oidc_service.fetch_user_org_code(userinfo, selected_role_id)
        smartcard_role_code, user_id = self.oidc_service.fetch_user_role_code(
            userinfo, selected_role_id, "R"
        )

        logger.info("Extracting user's organisation and smartcard codes")
        org_ods_codes = self.oidc_service.fetch_user_org_code(
            userinfo, selected_role_id
        )
        permitted_orgs_details = (
            self.ods_api_service.fetch_organisation_with_permitted_role(org_ods_codes)
        )

        logger.info("Calculating repository role")
        repository_role = self.generate_repository_role(
            permitted_orgs_details, smartcard_role_code
        )

        logger.info("Creating authorisation token")
        session_id = self.create_login_session(mock_id_token_claim_set)
        authorisation_token = self.issue_auth_token(
            session_id=session_id,
            id_token_claim_set=mock_id_token_claim_set,
            user_org_details=permitted_orgs_details,
            smart_card_role=smartcard_role_code,
            repository_role=repository_role.value,
            user_id=user_id,
        )

        logger.info("Returning authentication details")
        response = {
            "role": repository_role.value,
            "authorisation_token": authorisation_token,
        }
        logger.info(f"Response: {response}")
        return response

    def get_mock_user_info(self, username: str) -> dict:
        client_id, client_secret = self.obtain_credentials()
        session_state, code = self.authorize_user(
            username=username, client_id=client_id
        )
        access_token = self.get_access_token(code, client_id, client_secret)

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{self.base_mock_api_url}/realms/Cis2-mock-int/protocol/openid-connect/userinfo",
            headers=headers,
        )

        return response.json()

    def obtain_credentials(self):
        response = requests.get(
            "https://int.api.service.nhs.uk/mock-jwks/keycloak-client-credentials",
            headers={"apikey": self.mock_api_key},
        )
        response_data = response.json()
        print(response_data)
        client_id = response_data.get("cis2", {}).get("client_id")
        client_secret = response_data.get("cis2", {}).get("client_secret")
        print(client_id)
        print(client_secret)
        return client_id, client_secret

    def authorize_user(self, username: str, client_id: str):
        params = {
            "scope": "openid",
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": "https://example.org",
        }

        with requests.Session() as session:
            response = session.get(
                f"{self.base_mock_api_url}/realms/Cis2-mock-int/protocol/openid-connect/auth",
                params=params,
            )

            soup = BeautifulSoup(response.text, "html.parser")

            username_tag = soup.find(id="username")
            username_field_name = username_tag.get("name", "username")

            if not username_tag or not username_field_name:
                print("Couldn't find username field on page")
                return

            payload = {
                username_field_name: username,
            }

            action_url = soup.find("form")["action"]
            action_url = urljoin(response.url, action_url)

            response = session.post(action_url, data=payload, allow_redirects=True)

        parsed_url = urlparse(response.url)
        query_strings = parse_qs(parsed_url.query)

        session_state = query_strings.get("session_state", [None])[0]
        code = query_strings.get("code", [None])[0]

        print("session_state:", session_state)
        print("code:", code)

        return session_state, code

    def get_access_token(self, code: str, client_id: str, client_secret: str):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://example.org",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        response = requests.post(
            f"{self.base_mock_api_url}/realms/Cis2-mock-int/protocol/openid-connect/token",
            headers=headers,
            data=params,
        )

        data = response.json()
        access_token = data["access_token"]

        print(data)
        return access_token
