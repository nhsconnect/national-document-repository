from utils.audit_logging_setup import LoggingService

logger = LoggingService(__name__)


def get_bundle_entry(bundle, resource_type):
    for entry in bundle.entry:
        if entry.resource.resource_type == resource_type:
            return entry

    return None


def get_bundle_entries(bundle, resource_type) -> list:
    response = []
    for entry in bundle.entry:
        if entry.resource.resource_type == resource_type:
            response.append(entry)
    return response


def get_bundle_entries_of_multi_type(bundle, resource_types: list) -> dict:
    response = {}

    for entry in bundle.entry:
        resource_type = entry.resource.resource_type
        logger.info(resource_type)
        if resource_type in resource_types:
            resource_type_exists = response.get(resource_type, None)
            if resource_type_exists:
                response[resource_type].append(entry)
            else:
                response[resource_type] = [entry]

    return response


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
