import argparse

import boto3


def update_lambda_environment_variables(lambda_name, new_variables):
    session = boto3.Session()
    lambda_client = session.client("lambda")

    response = lambda_client.get_function_configuration(FunctionName=lambda_name)
    current_environment = response["Environment"]["Variables"]

    updated_environment = current_environment.copy()
    updated_environment.update(new_variables)

    lambda_client.update_function_configuration(
        FunctionName=lambda_name, Environment={"Variables": updated_environment}
    )


def retrieve_all_deployed_lambdas(environment):
    client = boto3.client("lambda")

    paginator = client.get_paginator("list_functions")

    response_iterator = paginator.paginate()

    all_functions = []
    for page in response_iterator:
        all_functions.extend(page["Functions"])

    lambdas_to_update = [
        func["FunctionName"]
        for func in all_functions
        if func["FunctionName"].startswith(f"{environment}")
    ]
    return lambdas_to_update


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Bulk Upload Script")

    parser.add_argument(
        "--environment",
        help="The name of the environment",
    )

    args = parser.parse_args()

    if not args.environment:
        args.environment = input("Please enter the name of the environment: ")
    lambdas_to_update = retrieve_all_deployed_lambdas(args.environment)
    variable = {"PDS_FHIR_IS_STUBBED": "false"}
    for lambda_function in lambdas_to_update:
        update_lambda_environment_variables(lambda_function, variable)
