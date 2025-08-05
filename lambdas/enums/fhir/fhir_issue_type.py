from enum import Enum


class FhirIssueCoding(Enum):
    INVALID = ("invalid", "Invalid Content")
    FORBIDDEN = ("forbidden", "Forbidden")
    NOT_FOUND = ("not-found", "Not Found")
    EXCEPTION = ("exception", "Exception")
    UNKNOWN = ("unknown", "Unknown User")

    def code(self):
        return self.value[0]

    def display(self):
        return self.value[1]
