import argparse
import json

import boto3


def invoke_lambda(lambda_name, payload={}):
    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=lambda_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    return json.loads(response["Payload"].read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Bulk Upload Script")

    parser.add_argument(
        "--environment",
        help="The name of the environment",
    )
    parser.add_argument(
        "--start-bulk-upload",
        action="store_true",
        help="Start the Bulk Upload",
    )

    args = parser.parse_args()

    if not args.environment:
        args.environment = input("Please enter the name of the environment: ")

    if args.start_bulk_upload or input(
        "Would you like to start the Bulk Upload Process:"
    ):
        invoke_lambda(f"{args.environment}_V2BulkUploadMetadataLambda")
