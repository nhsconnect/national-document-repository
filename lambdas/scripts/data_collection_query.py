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


def decimal_default(obj):
    """Helper function to convert Decimals to floats for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, set):
        # Handle sets by converting them to lists
        return list(obj)
    elif hasattr(obj, "__dict__"):
        # Handle other custom objects by serializing their dictionary
        return obj.__dict__
    else:
        raise TypeError(f"Object of type {type(obj)} is not serializable")


def convert_to_dict(item):
    """Converts an item to a dictionary if it is a dataclass, else returns the item as is."""
    if is_dataclass(item):
        return asdict(item)
    else:
        return item  # Handle custom objects if needed


def main():
    service = DataCollectionService()

    # Collect all data
    statistic_data = service.collect_all_data()

    # Convert all dataclasses to dictionaries if they are dataclass instances
    statistic_data_dict = [convert_to_dict(entry) for entry in statistic_data]

    # Convert the data to a JSON string, handling Decimals
    json_output = json.dumps(statistic_data_dict, default=decimal_default, indent=4)

    # Log or print the JSON output
    print(json_output)

    # If you want to write to a file
    with open("output.json", "w") as f:
        f.write(json_output)


if __name__ == "__main__":
    main()
