from services.document_service import DocumentService
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


class UploadConfirmResultService:
    def __init__(self):
        self.document_service = DocumentService()


#  check doc references against dynamo tables to see if ARF or LG- check if this is done elsewhere already
#  if LG then validate - use existing util function
#  copy files to relevant bucket with NHS number prefixed as a folder - check if this done elsewhere already
#  update relevant metadata table - set UpdateStatus to true - is this correct name?
# return 204 if all files processed successfully
