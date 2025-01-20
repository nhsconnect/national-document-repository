from typing import List, Literal, Optional

from enums.snomed_codes import SnomedCode, SnomedCodes
from models.fhir.R4.base_models import (
    CodeableConcept,
    Coding,
    Extension,
    Period,
    Reference,
)
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class NRLFormatCode(Coding):
    system: Literal["https://fhir.nhs.uk/England/CodeSystem/England-NRLFormatCode"] = (
        "https://fhir.nhs.uk/England/CodeSystem/England-NRLFormatCode"
    )
    code: Literal["urn:nhs-ic:record-contact", "urn:nhs-ic:unstructured"] = (
        "urn:nhs-ic:unstructured"
    )
    display: Literal["Contact details (HTTP Unsecured)", "Unstructured Document"] = (
        "Unstructured document"
    )


class Attachment(BaseModel):
    contentType: str = "application/pdf"
    language: str = "en-GB"
    url: Optional[str] = None
    size: Optional[int] = None
    hash: Optional[str] = None
    title: Optional[str] = None
    creation: Optional[str] = None


class ContentStabilityExtensionCoding(Coding):
    system: Literal[
        "https://fhir.nhs.uk/England/CodeSystem/England-NRLContentStability"
    ] = "https://fhir.nhs.uk/England/CodeSystem/England-NRLContentStability"
    code: Literal["static", "dynamic"] = "static"
    display: Literal["Static", "Dynamic"] = "Static"


class ContentStabilityExtensionValueCodeableConcept(CodeableConcept):
    coding: List[ContentStabilityExtensionCoding] = [ContentStabilityExtensionCoding()]


class ContentStabilityExtension(Extension):
    url: Literal[
        "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-ContentStability"
    ] = "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-ContentStability"
    valueCodeableConcept: ContentStabilityExtensionValueCodeableConcept = (
        ContentStabilityExtensionValueCodeableConcept()
    )


class DocumentReferenceContent(BaseModel):
    attachment: Attachment
    format: NRLFormatCode = NRLFormatCode()
    extension: List[ContentStabilityExtension] = [ContentStabilityExtension()]


class DocumentReferenceContext(BaseModel):
    encounter: Optional[List[Reference]] = None
    event: Optional[List[CodeableConcept]] = None
    period: Optional[Period] = None
    facilityType: Optional[CodeableConcept] = None
    practiceSetting: CodeableConcept
    sourcePatientInfo: Optional[Reference] = None
    related: Optional[List[Reference]] = None


class DocumentReference(BaseModel):
    resourceType: Literal["DocumentReference"] = "DocumentReference"
    status: Literal["current"] = "current"
    type: Optional[CodeableConcept] = None
    category: Optional[List[CodeableConcept]] = None
    subject: Optional[Reference] = None
    date: Optional[str] = None
    author: Optional[List[Reference]] = None
    authenticator: Optional[Reference] = None
    custodian: Optional[Reference] = None
    content: List[DocumentReferenceContent]
    context: Optional[DocumentReferenceContext] = None


class DocumentReferenceInfo(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    nhs_number: str
    custodian: str
    snomed_code_doc_type: SnomedCode = SnomedCodes.LLOYD_GEORGE.value
    snomed_code_category: SnomedCode = SnomedCodes.CARE_PLAN.value
    snomed_code_practice_setting: SnomedCode = (
        SnomedCodes.GENERAL_MEDICAL_PRACTICE.value
    )
    attachment: Optional[Attachment] = Attachment()

    def create_fhir_document_reference_object(self):
        fhir_base_url = "https://fhir.nhs.uk/Id"
        snomed_url = "http://snomed.info/sct"

        fhir_document_ref = DocumentReference(
            subject={
                "identifier": {
                    "system": fhir_base_url + "/nhs-number",
                    "value": self.nhs_number,
                }
            },
            custodian={
                "identifier": {
                    "system": fhir_base_url + "/ods-organization-code",
                    "value": self.custodian,
                },
            },
            type={
                "coding": [
                    {
                        "system": snomed_url,
                        "code": self.snomed_code_doc_type.code,
                        "display": self.snomed_code_doc_type.display_name,
                    }
                ]
            },
            content=[{"attachment": self.attachment}],
            category=[
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
            author=[
                {
                    "identifier": {
                        "system": fhir_base_url + "/ods-organization-code",
                        "value": self.custodian,
                    }
                }
            ],
            context={
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
        )
        return fhir_document_ref
