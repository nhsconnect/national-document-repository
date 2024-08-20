from services.edge_presign_service import edge_presign_service
from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def lambda_handler(event, context):

    request = event["Records"][0]["cf"]["request"]
    requested_url = request["uri"]
    logger.info(f"Info: URL Requested [{requested_url}]")

    table_name = "ndrd_CloudFrontEdgeReference"
    edge_presign_service.attempt_url_update(table_name, requested_url)
    return request
