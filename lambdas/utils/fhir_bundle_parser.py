from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def map_bundle_entries_to_dict(bundle) -> dict:
    response = {}

    for entry in bundle.entry:
        resource_type = entry.resource.resource_type
        resource_type_exists = response.get(resource_type, None)
        if resource_type_exists:
            response[resource_type].append(entry)
        else:
            response[resource_type] = [entry]

    return response
