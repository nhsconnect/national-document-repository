from enum import Enum


class LoggingAppInteraction(Enum):
    LOGIN = "Login"
    PATIENT_SEARCH = "Patient search"
    VIEW_PATIENT = "View Patient"
    VIEW_LG_RECORD = "View LG record"
    DOWNLOAD_RECORD = "Download a record"
    DELETE_RECORD = "Delete a record"
    UPLOAD_RECORD = "Upload a record"
    LOGOUT = "Logout"
    SEND_FEEDBACK = "Send feedback"
    FEATURE_FLAGS = "Feature flags"
    UPLOAD_CONFIRMATION = "Upload confirmation"
