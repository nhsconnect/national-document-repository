import argparse
import json
import sys

import boto3


def invoke_lambda(lambda_name, payload={}):
    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=lambda_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )
    return json.loads(response["Payload"].read())


def update_lambda_environment_variables(lambda_name, new_variable):
    session = boto3.Session()
    lambda_client = session.client("lambda")

    response = lambda_client.get_function_configuration(FunctionName=lambda_name)
    current_environment = response["Environment"]["Variables"]
    if current_environment.get("PDS_FHIR_IS_STUBBED"):
        updated_environment = current_environment.copy()
        updated_environment.update(new_variable)

        lambda_client.update_function_configuration(
            FunctionName=lambda_name, Environment={"Variables": updated_environment}
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Bulk Upload Script")

    parser.add_argument(
        "--environment",
        help="The name of the environment",
    )
    parser.add_argument(
        "--disable-pds-stub",
        action="store_true",
        help="Disable the PDS Stub",
    )
    parser.add_argument(
        "--start-bulk-upload",
        action="store_true",
        help="Start the Bulk Upload",
    )

    args = parser.parse_args()

    if not args.environment:
        args.environment = input("Please enter the name of the environment: ")

    client = boto3.client("lambda")

    response = client.list_functions()

    lambda_to_update = [
        func["FunctionName"]
        for func in response["Functions"]
        if func["FunctionName"].startswith(f"{args.environment}_")
    ]

    if args.disable_pds_stub or (
        sys.stdin.isatty()
        and input("Would you like to disable the FHIR Stub: ").lower() == "y"
    ):
        new_variable = {"PDS_FHIR_IS_STUBBED": "false"}
        for i in lambda_to_update:
            update_lambda_environment_variables(i, new_variable)
    if args.start_bulk_upload or input(
        "Would you like to start the Bulk Upload Process:"
    ):
        invoke_lambda(f"{args.environment}_BulkUploadMetadataLambda")
