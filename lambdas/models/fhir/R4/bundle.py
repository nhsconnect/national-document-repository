from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from models.fhir.R4.base_models import Identifier, Link
from pydantic import BaseModel, Field


class BundleEntrySearch(BaseModel):
    mode: Optional[Literal["match", "include", "outcome"]] = None
    score: Optional[float] = None


class BundleEntryRequest(BaseModel):
    method: Literal["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"] = Field(...)
    url: str = Field(...)
    ifNoneMatch: Optional[str] = None
    ifModifiedSince: Optional[datetime] = None
    ifMatch: Optional[str] = None
    ifNoneExist: Optional[str] = None


class BundleEntryResponse(BaseModel):
    status: str = Field(...)
    location: Optional[str] = None
    etag: Optional[str] = None
    lastModified: Optional[datetime] = None
    outcome: Optional[Dict[str, Any]] = None


class BundleEntry(BaseModel):
    fullUrl: Optional[str] = None
    resource: Optional[Dict[str, Any]] = None
    search: Optional[BundleEntrySearch] = None
    request: Optional[BundleEntryRequest] = None
    response: Optional[BundleEntryResponse] = None


class Signature(BaseModel):
    type: List[Dict[str, Any]] = Field(...)
    when: datetime = Field(...)
    who: Dict[str, Any] = Field(...)
    targetFormat: Optional[str] = None
    sigFormat: Optional[str] = None
    data: Optional[str] = None


class Bundle(BaseModel):
    resourceType: Literal["Bundle"] = "Bundle"
    identifier: Optional[Identifier] = None
    type: Literal[
        "document",
        "message",
        "transaction",
        "transaction-response",
        "batch",
        "batch-response",
        "history",
        "searchset",
        "collection",
    ] = Field(...)
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
    )
    total: Optional[int] = None
    link: Optional[List[Link]] = None
    entry: Optional[List[BundleEntry]] = None
    signature: Optional[Signature] = None
