from enum import Enum


class FHIR_RESOURCE_TYPES(str, Enum):
    MessageHeader = "MessageHeader"
    Patient = "Patient"
    Organisation = "Organization"
