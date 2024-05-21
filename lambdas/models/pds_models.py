from datetime import date
from typing import Optional

from models.config import conf
from pydantic import BaseModel


class Period(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None


class Address(BaseModel):
    model_config = conf

    use: str
    period: Optional[Period] = None
    postal_code: str = ""


class Name(BaseModel):
    use: str
    period: Optional[Period] = None
    given: list[str] = [""]
    family: str


class Security(BaseModel):
    code: str
    display: str


class Meta(BaseModel):
    versionId: str
    security: list[Security]


class GPIdentifier(BaseModel):
    system: str = ""
    value: str
    period: Optional[Period] = None


class GeneralPractitioner(BaseModel):
    id: str = ""
    type: str = ""
    identifier: GPIdentifier


class PatientDetails(BaseModel):
    model_config = conf

    given_name: list[str] = [""]
    family_name: str = ""
    birth_date: Optional[date] = None
    postal_code: str = ""
    nhs_number: str
    superseded: bool
    restricted: bool
    general_practice_ods: str = ""
    active: Optional[bool] = None


class Patient(BaseModel):
    model_config = conf

    id: str
    birth_date: date
    address: list[Address] = []
    name: list[Name]
    meta: Meta
    general_practitioner: Optional[list[GeneralPractitioner]] = None

    def get_security(self) -> Security:
        security = self.meta.security[0] if self.meta.security[0] else None
        if not security:
            raise ValueError("No valid security found in patient meta")

        return security

    def is_unrestricted(self) -> bool:
        security = self.get_security()
        return security.code == "U"

    def get_current_usual_name(self) -> Optional[Name]:
        for entry in self.name:
            if entry.use.lower() == "usual":
                return entry

    def get_current_home_address(self) -> Optional[Address]:
        if self.is_unrestricted() and self.address:
            for entry in self.address:
                if entry.use.lower() == "home":
                    return entry

    def get_active_ods_code_for_gp(self) -> str:
        if self.general_practitioner:
            for entry in self.general_practitioner:
                period = entry.identifier.period
                gp_end_date = period.end if period else None
                if not gp_end_date or gp_end_date >= date.today():
                    return entry.identifier.value
        return ""

    def get_is_active_status(self) -> bool:
        gp_ods = self.get_active_ods_code_for_gp()
        return bool(gp_ods)

    def get_patient_details(self, nhs_number) -> PatientDetails:
        current_usual_name = self.get_current_usual_name()
        given_name = current_usual_name.given if current_usual_name else [""]
        family_name = current_usual_name.family if current_usual_name else ""
        current_home_address = self.get_current_home_address()

        patient_details = PatientDetails(
            givenName=given_name,
            familyName=family_name,
            birthDate=self.birth_date,
            postalCode=(
                current_home_address.postal_code
                if self.is_unrestricted() and current_home_address
                else ""
            ),
            nhsNumber=self.id,
            superseded=bool(nhs_number == id),
            restricted=not self.is_unrestricted(),
            generalPracticeOds=self.get_active_ods_code_for_gp(),
            active=self.get_is_active_status(),
        )

        return patient_details

    def get_minimum_patient_details(self, nhs_number) -> PatientDetails:
        current_usual_name = self.get_current_usual_name()
        given_name = current_usual_name.given if current_usual_name else [""]
        family_name = current_usual_name.family if current_usual_name else ""

        return PatientDetails(
            givenName=given_name,
            familyName=family_name,
            birthDate=self.birth_date,
            generalPracticeOds=(
                self.get_active_ods_code_for_gp() if self.is_unrestricted() else ""
            ),
            nhsNumber=self.id,
            superseded=bool(nhs_number == id),
            restricted=not self.is_unrestricted(),
        )
