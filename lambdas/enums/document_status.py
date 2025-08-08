from enum import Enum


class DocumentStatus(Enum):
    CANCELLED = ("cancelled", "UC_4002")
    FORBIDDEN = ("forbidden", "UC_4003")
    NOT_FOUND = ("not-found", "UC_4004")
    INFECTED = ("infected", "UC_4005")

    @property
    def code(self):
        return self.value[1]

    @property
    def display(self):
        return self.value[0]
