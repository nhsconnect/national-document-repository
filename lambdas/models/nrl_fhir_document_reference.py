from typing import Optional

from enums.snomed_codes import SnomedCode, SnomedCodes
from fhir.resources.R4B.documentreference import DocumentReference
from models.nrl_sqs_message import NrlAttachment
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FhirDocumentReference(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    nhs_number: str
    custodian: str
    snomed_code_doc_type: SnomedCode = SnomedCodes.LLOYD_GEORGE.value
    snomed_code_category: SnomedCode = SnomedCodes.CARE_PLAN.value
    snomed_code_practice_setting: SnomedCode = (
        SnomedCodes.GENERAL_MEDICAL_PRACTICE.value
    )
    attachment: Optional[NrlAttachment] = NrlAttachment()

    def build_fhir_dict(self):
        snomed_url = "http://snomed.info/sct"
        fhir_base_url = "https://fhir.nhs.uk/Id"
        structure_json = {
            "status": "current",
            "subject": {
                "identifier": {
                    "system": fhir_base_url + "/nhs-number",
                    "value": self.nhs_number,
                }
            },
            "custodian": {
                "identifier": {
                    "system": fhir_base_url + "/ods-organization-code",
                    "value": self.custodian,
                }
            },
            "type": {
                "coding": [
                    {
                        "system": snomed_url,
                        "code": self.snomed_code_doc_type.code,
                        "display": self.snomed_code_doc_type.display_name,
                    }
                ]
            },
            "category": [
                {
                    "coding": [
                        {
                            "system": snomed_url,
                            "code": self.snomed_code_category.code,
                            "display": self.snomed_code_category.display_name,
                        }
                    ]
                }
            ],
            "author": [
                {
                    "identifier": {
                        "system": fhir_base_url + "/ods-organization-code",
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
            "context": {
                "practiceSetting": {
                    "coding": [
                        {
                            "system": snomed_url,
                            "code": self.snomed_code_practice_setting.code,
                            "display": self.snomed_code_practice_setting.display_name,
                        }
                    ]
                }
            },
        }
        return DocumentReference(**structure_json)
