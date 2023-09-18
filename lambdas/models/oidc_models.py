from typing import TypeAlias

from pydantic import BaseModel

AccessToken: TypeAlias = str


class IdTokenClaimSet(BaseModel):
    sub: str
    sid: str
    exp: int
