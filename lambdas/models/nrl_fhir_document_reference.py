from fhir.resources.R4B.documentreference import DocumentReference
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FhirDocumentReference(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    nhs_number: str
    custodian: str = "None"
    snomed_code_doc_type: str = "None"
    snomed_code_category: str = "None"

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
                    "attachment": {
                        "contentType": "application/pdf",
                        "language": "en-US",
                        "url": "https://spine-proxy.national.ncrs.nhs.uk/https%3A%2F%2Fp1.nhs.uk%2FMentalhealthCrisisPlanReport.pdf",
                        "size": 3654,
                        "hash": "2jmj7l5rSw0yVb/vlWAYkK/YBwk=",
                        "title": "Mental health crisis plan report",
                        "creation": "2022-12-21T10:45:41+11:00",
                    },
                    "format": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-NRLFormatCode",
                        "code": "urn:nhs-ic:unstructured",
                        "display": "Unstructured document",
                    },
                }
            ],
        }
        return DocumentReference(**example)
