from enum import Enum


class FhirIssueCoding(Enum):
    INVALID = ("Invalid", "Invalid")
    FORBIDDEN = ("forbidden", "Forbidden")
    NOT_FOUND = ("not-found", "Not Found")
    EXCEPTION = ("exception", "Exception")

    def code(self):
        return self.value[0]

    def display(self):
        return self.value[1]
