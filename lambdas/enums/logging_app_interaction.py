from enum import Enum


class LoggingAppInteraction(Enum):
    LOGIN = "Login"
    PATIENT_SEARCH = "Patient search"
    VIEW_PATIENT = "View Patient"
    VIEW_LG_RECORD = "View LG record"
    DOWNLOAD_RECORD = "Downloaded record"
    DELETE_RECORD = "Delete a record"
    UPLOAD_RECORD = "Uploaded record"
    LOGOUT = "Logout"
