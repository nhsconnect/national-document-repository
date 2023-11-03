from datetime import date
from typing import Optional

from models.config import conf
from pydantic import BaseModel


class Period(BaseModel):
    start: date = None
    end: Optional[date] = None


class Address(BaseModel):
    model_config = conf

    use: str
    period: Period
    postal_code: Optional[str] = ""


class Name(BaseModel):
    use: str
    period: Period
    given: list[str]
    family: str


class Security(BaseModel):
    code: str
    display: str


class Meta(BaseModel):
    versionId: str
    security: list[Security]


class GPIdentifier(BaseModel):
    system: Optional[str]
    value: str
    period: Optional[Period]


class GeneralPractitioner(BaseModel):
    id: Optional[str]
    type: Optional[str]
    identifier: GPIdentifier


class PatientDetails(BaseModel):
    model_config = conf

    given_Name: Optional[list[str]] = []
    family_name: Optional[str] = ""
    birth_date: Optional[date] = None
    postal_code: Optional[str] = ""
    nhs_number: str
    superseded: bool
    restricted: bool
    general_practice_ods: Optional[str] = ""
    active: bool = False


class Patient(BaseModel):
    model_config = conf

    id: str
    birth_date: date
    address: Optional[list[Address]] = []
    name: list[Name]
    meta: Meta
    general_practitioner: Optional[list[GeneralPractitioner]] = []

    def get_security(self) -> Security:
        security = self.meta.security[0] if self.meta.security[0] else None
        if not security:
            raise ValueError("No valid security found in patient meta")

        return security

    def is_unrestricted(self) -> bool:
        security = self.get_security()
        if security.code == "U":
            return True
        return False

    def get_current_usual_name(self) -> [Optional[Name]]:
        for entry in self.name:
            if entry.use.lower() == "usual":
                return entry

    def get_current_home_address(self) -> Optional[Address]:
        if self.is_unrestricted():
            for entry in self.address:
                if entry.use.lower() == "home":
                    return entry

    def get_ods_code_for_gp(self) -> str:
        for entry in self.general_practitioner:
            gp_end_date = entry.identifier.period.end
            if not gp_end_date or gp_end_date >= date.today():
                return entry.identifier.value
        raise ValueError("No active GP practice for the patient")

    def get_patient_details(self, nhs_number) -> PatientDetails:
        patient_details = PatientDetails(
            givenName=self.get_current_usual_name().given,
            familyName=self.get_current_usual_name().family,
            birthDate=self.birth_date,
            postalCode=self.get_current_home_address().postal_code
            if self.is_unrestricted()
            else "",
            nhsNumber=self.id,
            superseded=bool(nhs_number == id),
            restricted=not self.is_unrestricted(),
            generalPracticeOds=self.get_ods_code_for_gp(),
            active = False
        )
        
        patient_details.active = patient_details.general_practice_ods != ""
        return patient_details

    def get_minimum_patient_details(self, nhs_number) -> PatientDetails:
        return PatientDetails(
            givenName=self.get_current_usual_name().given,
            familyName=self.get_current_usual_name().family,
            birthDate=self.birth_date,
            generalPracticeOds=self.get_ods_code_for_gp()
            if self.is_unrestricted()
            else "",
            nhsNumber=self.id,
            superseded=bool(nhs_number == id),
            restricted=not self.is_unrestricted(),
        )
