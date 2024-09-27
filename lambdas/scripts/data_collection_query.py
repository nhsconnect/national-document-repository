import json
import os
from dataclasses import asdict, is_dataclass
from decimal import Decimal

from services.data_collection_service import DataCollectionService

os.environ["WORKSPACE"] = ""
os.environ["STATISTICS_TABLE"] = ""
os.environ["DOCUMENT_STORE_DYNAMODB_NAME"] = ""
os.environ["LLOYD_GEORGE_DYNAMODB_NAME"] = ""
os.environ["LLOYD_GEORGE_BUCKET_NAME"] = ""
os.environ["DOCUMENT_STORE_BUCKET_NAME"] = ""


def check_env_vars(required_vars):
    missing_vars = [var for var in required_vars if not os.getenv(var)]
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
    required_env_vars = [
        "WORKSPACE",
        "STATISTICS_TABLE",
        "DOCUMENT_STORE_DYNAMODB_NAME",
        "LLOYD_GEORGE_DYNAMODB_NAME",
        "LLOYD_GEORGE_BUCKET_NAME",
        "DOCUMENT_STORE_BUCKET_NAME",
    ]
    check_env_vars(required_env_vars)

    service = DataCollectionService()
    statistic_data = service.collect_all_data()
    statistic_data_dict = [convert_to_dict(entry) for entry in statistic_data]
    json_output = json.dumps(statistic_data_dict, default=decimal_default, indent=4)
    print(json_output)
    with open("data_collection_output.json", "w") as f:
        f.write(json_output)


if __name__ == "__main__":
    main()
