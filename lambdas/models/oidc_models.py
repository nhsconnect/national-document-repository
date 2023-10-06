from typing import TypeAlias

from pydantic import BaseModel

AccessToken: TypeAlias = str


class IdTokenClaimSet(BaseModel):
    sub: str  # subject claim. user's login ID at CIS2
    sid: str  # user's session ID at CIS2
    exp: int  # token expiry time
