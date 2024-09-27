import json
import os
from dataclasses import asdict, is_dataclass
from decimal import Decimal

from services.data_collection_service import DataCollectionService

os.environ["WORKSPACE"] = "ndr-dev"
os.environ["STATISTICS_TABLE"] = "ndr-dev_ApplicationStatistics"
os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = "ndr-dev_DocumentReferenceMetadata"
os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = "ndr-dev_LloydGeorgeReferenceMetadata"
os.environ["LLOYD_GEORGE_BUCKET_NAME"] = "ndr-dev-lloyd-george-store"
os.environ["DOCUMENT_STORE_BUCKET_NAME"] = "ndr-dev-ndr-document-store"

# README:
# Fill in above environment variables then run the following

# make env
# source ./lambdas/venv/bin/activate
# PYTHONPATH=lambdas/. python3 lambdas/scripts/data_collection_query.py


def check_env_vars():
    required_env = [
        "WORKSPACE",
        "STATISTICS_TABLE",
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "DOCUMENT_STORE_BUCKET_NAME",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "AWS_REGION",
    ]
    missing_vars = [var for var in required_env if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        raise TypeError(f"Object of type {type(obj)} is not serializable")


def convert_to_dict(item):
    if is_dataclass(item):
        return asdict(item)
    else:
        return item


def main():
    check_env_vars()

    service = DataCollectionService()
    statistic_data = service.collect_all_data()
    statistic_data_dict = [convert_to_dict(entry) for entry in statistic_data]
    json_output = json.dumps(statistic_data_dict, default=decimal_default, indent=4)
    print(json_output)
    with open("data_collection_output.json", "w") as f:
        f.write(json_output)


if __name__ == "__main__":
    main()
