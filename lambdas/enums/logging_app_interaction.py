from enum import Enum


class LoggingAppInteraction(Enum):
    LOGIN = "Login"
    EDGE_PRESIGN = "Edge Presign Cloudfront URL"
    PATIENT_SEARCH = "Patient search"
    VIEW_PATIENT = "View Patient"
    VIEW_LG_RECORD = "View LG record"
    DOWNLOAD_RECORD = "Download a record"
    DELETE_RECORD = "Delete a record"
    UPLOAD_RECORD = "Upload a record"
    LOGOUT = "Logout"
    SEND_FEEDBACK = "Send feedback"
    FEATURE_FLAGS = "Feature flags"
    VIRUS_SCAN = "Virus Scan"
    UPLOAD_CONFIRMATION = "Upload confirmation"
    UPDATE_UPLOAD_STATE = "Update upload state"
