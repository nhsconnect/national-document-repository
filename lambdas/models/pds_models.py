from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


def to_camel(string: str) -> str:
    string_split = string.split("_")
    return string_split[0] + "".join(word.capitalize() for word in string_split[1:])


conf = ConfigDict(alias_generator=to_camel)


class Period(BaseModel):
    start: str
    end: str


class Address(BaseModel):
    model_config = conf

    use: str
    period: Period
    postal_code: str


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


class PatientDetails(BaseModel):
    model_config = conf

    given_Name: Optional[list[str]] = []
    family_name: Optional[str] = ""
    birth_date: Optional[str] = ""
    postal_code: Optional[str] = ""
    nhs_number: str
    superseded: bool
    restricted: bool


class Patient(BaseModel):
    model_config = conf

    id: str
    birth_date: str
    address: Optional[list[Address]] = []
    name: list[Name]
    meta: Meta

    def get_security(self) -> Security:
        security = self.meta.security[0] if self.meta.security[0] else None
        if not security:
            raise ValidationError("No valid security found in patient meta")

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

    def get_patient_details(self, nhs_number) -> PatientDetails:
        return PatientDetails(
            givenName=self.get_current_usual_name().given,
            familyName=self.get_current_usual_name().family,
            birthDate=self.birth_date,
            postalCode=self.get_current_home_address().postal_code
            if self.is_unrestricted()
            else "",
            nhsNumber=self.id,
            superseded=bool(nhs_number == id),
            restricted=not self.is_unrestricted(),
        )
