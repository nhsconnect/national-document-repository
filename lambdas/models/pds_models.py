from datetime import date
from typing import Optional, Tuple

from enums.death_notification_status import DeathNotificationStatus
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)
conf = ConfigDict(alias_generator=to_camel)


class Period(BaseModel):
    start: date
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

    def is_currently_in_use(self) -> bool:
        if not self.period:
            return False
        if self.use.lower() in ["nickname", "old"]:
            return False

        today = date.today()

        name_started_already = self.period.start <= today
        name_not_expired_yet = (not self.period.end) or self.period.end >= today

        return name_started_already and name_not_expired_yet


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


class Extension(BaseModel):
    url: str
    extension: list[dict] = []


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
    deceased: bool = False
    death_notification_status: Optional[DeathNotificationStatus] = None


class Patient(BaseModel):
    model_config = conf

    id: str
    birth_date: Optional[date] = None
    address: list[Address] = []
    name: list[Name]
    meta: Meta
    general_practitioner: list[GeneralPractitioner] = []
    deceased_date_time: str = ""
    extension: list[Extension] = []

    def get_security(self) -> Security:
        security = self.meta.security[0] if self.meta.security[0] else None
        if not security:
            raise ValueError("No valid security found in patient meta")

        return security

    def is_unrestricted(self) -> bool:
        security = self.get_security()
        return security.code == "U"

    def get_usual_name(self) -> Optional[Name]:
        for entry in self.name:
            if entry.use.lower() == "usual":
                return entry

    def get_most_recent_name(self) -> Optional[Name]:
        active_names = [name for name in self.name if name.is_currently_in_use()]
        if not active_names:
            return None

        sorted_by_start_date_desc = sorted(
            active_names, key=lambda name: name.period.start, reverse=True
        )
        return sorted_by_start_date_desc[0]

    def get_current_family_name_and_given_name(self) -> Tuple[str, list[str]]:
        current_name = self.get_most_recent_name() or self.get_usual_name()
        if not current_name:
            logger.warning(
                "The patient does not have a currently active name or a usual name."
            )
            return "", [""]

        given_name = current_name.given
        family_name = current_name.family

        if not given_name or given_name == [""]:
            logger.warning("The given name of patient is empty.")

        return family_name, given_name

    def get_current_home_address(self) -> Optional[Address]:
        if self.is_unrestricted() and self.address:
            for entry in self.address:
                if entry.use.lower() == "home":
                    return entry

    def get_active_ods_code_for_gp(self) -> str:
        for entry in self.general_practitioner:
            period = entry.identifier.period
            if not period:
                continue
            gp_end_date = period.end
            if not gp_end_date or gp_end_date >= date.today():
                return entry.identifier.value
        return ""

    def get_is_active_status(self) -> bool:
        gp_ods = self.get_active_ods_code_for_gp()
        return bool(gp_ods)

    def get_death_notification_status(self) -> Optional[DeathNotificationStatus]:
        if not self.deceased_date_time:
            return None

        for extension_wrapper in self.extension:
            if (
                extension_wrapper.url
                != "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus"
            ):
                continue
            return self.parse_death_notification_status_extension(extension_wrapper)

    @staticmethod
    def parse_death_notification_status_extension(
        extension_wrapper: Extension,
    ) -> Optional[DeathNotificationStatus]:
        try:
            for nested_extension in extension_wrapper.extension:
                if nested_extension["url"] == "deathNotificationStatus":
                    return DeathNotificationStatus.from_code(
                        nested_extension["valueCodeableConcept"]["coding"][0]["code"]
                    )
        except (KeyError, IndexError, ValueError) as e:
            logger.info(
                "Failed to parse death_notification_status "
                "for patient due to error: %s. Will fill the value as None.",
                e,
            )
        return None

    def get_patient_details(self, nhs_number) -> PatientDetails:
        family_name, given_name = self.get_current_family_name_and_given_name()
        current_home_address = self.get_current_home_address()
        death_notification_status = self.get_death_notification_status()

        patient_details = PatientDetails(
            givenName=given_name,
            familyName=family_name,
            birthDate=self.birth_date,
            postalCode=(
                current_home_address.postal_code if current_home_address else ""
            ),
            nhsNumber=self.id,
            superseded=bool(nhs_number == id),
            restricted=not self.is_unrestricted(),
            generalPracticeOds=self.get_active_ods_code_for_gp(),
            active=self.get_is_active_status(),
            deceased=is_deceased(death_notification_status),
            deathNotificationStatus=death_notification_status,
        )

        return patient_details

    def get_minimum_patient_details(self, nhs_number) -> PatientDetails:
        family_name, given_name = self.get_current_family_name_and_given_name()
        death_notification_status = self.get_death_notification_status()

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
            deathNotificationStatus=death_notification_status,
            deceased=is_deceased(death_notification_status),
        )


def is_deceased(death_notification_status: Optional[DeathNotificationStatus]) -> bool:
    return (
        death_notification_status == DeathNotificationStatus.FORMAL
        or death_notification_status == DeathNotificationStatus.INFORMAL
    )
