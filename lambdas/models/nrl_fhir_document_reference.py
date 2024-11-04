import os
from typing import Optional

from fhir.resources.R4B.documentreference import DocumentReference
from models.nrl_sqs_message import NrlAttachment
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FhirDocumentReference(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    nhs_number: str
    custodian: str = os.getenv("NRL_END_USER_ODS_CODE", "")
    snomed_code_doc_type: str = "None"
    snomed_code_category: str = "None"
    attachment: Optional[NrlAttachment] = {}

    def build_fhir_dict(self):
        example = {
            "status": "current",
            "subject": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/nhs-number",
                    "value": self.nhs_number,
                }
            },
            "custodian": {
                "identifier": {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": self.custodian,
                }
            },
            "type": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": self.snomed_code_doc_type,
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": self.snomed_code_category,
                            "display": "Care plan",
                        }
                    ]
                }
            ],
            "author": [
                {
                    "identifier": {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": self.custodian,
                    }
                }
            ],
            "content": [
                {
                    "attachment": self.attachment.model_dump(
                        by_alias=True, exclude_none=True, exclude_defaults=True
                    ),
                    "format": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-NRLFormatCode",
                        "code": "urn:nhs-ic:unstructured",
                        "display": "Unstructured document",
                    },
                }
            ],
        }
        return DocumentReference(**example)
