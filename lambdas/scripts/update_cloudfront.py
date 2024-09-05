import os
import sys
import time

import boto3
from botocore.exceptions import ClientError

# Get environment variables
distribution_id = os.getenv("DISTRIBUTION_ID")
lambda_name = os.getenv("LAMBDA_NAME")
aws_region = os.getenv("AWS_REGION")
aws_account_id = os.getenv("AWS_ACCOUNT_ID")

# Initialize AWS clients
cloudfront_client = boto3.client("cloudfront", region_name=aws_region)
lambda_client = boto3.client("lambda", region_name=aws_region)
sts_client = boto3.client("sts", region_name=aws_region)


def get_aws_account_id():
    response = sts_client.get_caller_identity()
    account_id = response["Account"]
    print("Retrieved AWS Account ID: ***")
    return account_id


def get_latest_lambda_version(function_name):
    print(f"Getting latest version for Lambda function: {function_name}")
    response = lambda_client.list_versions_by_function(FunctionName=function_name)
    versions = response["Versions"]
    versions = [v for v in versions if v["Version"] != "$LATEST"]
    latest_version = max(versions, key=lambda x: int(x["Version"]))
    print(f"Latest Lambda version: {latest_version['Version']}")
    return latest_version["Version"]


def check_lambda_status(function_name, version):
    print(f"Checking status of Lambda function {function_name} version {version}")
    while True:
        response = lambda_client.get_function(
            FunctionName=function_name, Qualifier=version
        )
        status = response["Configuration"]["State"]
        print(f"Lambda function status: {status}")
        if status == "Active":
            break
        print("Lambda function not yet active. Retrying in 30 seconds...")
        time.sleep(30)


def update_cloudfront_lambda_association(distribution_id, lambda_arn):
    print(
        f"Updating CloudFront distribution: {distribution_id} with Lambda function ARN: {lambda_arn}"
    )
    try:
        response = cloudfront_client.get_distribution_config(Id=distribution_id)
        distribution_config = response["DistributionConfig"]
        etag = response["ETag"]

        # Check if 'Items' exist in 'LambdaFunctionAssociations'
        lambda_associations = distribution_config["DefaultCacheBehavior"].get(
            "LambdaFunctionAssociations", {}
        )
        items = lambda_associations.get("Items", [])

        if not items:
            print(
                f"Error for distribution '{distribution_id}'. Lambda associations not found. "
                "Manually clean any duplicated and unused distributions and try again."
            )
            sys.exit(1)

        for item in items:
            if item["EventType"] in [
                "viewer-request",
                "viewer-response",
                "origin-request",
                "origin-response",
            ]:
                print(f"Updating LambdaFunctionARN for event type {item['EventType']}")
                item["LambdaFunctionARN"] = lambda_arn

        cloudfront_client.update_distribution(
            Id=distribution_id, DistributionConfig=distribution_config, IfMatch=etag
        )
        print(
            f"Updated CloudFront distribution '{distribution_id}' to use Lambda '{lambda_arn}'."
        )

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchDistribution":
            print(f"Distribution '{distribution_id}' does not exist. Skipping update.")
        else:
            print(f"Error updating distribution: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Get AWS Account ID
        if not aws_account_id:
            aws_account_id = get_aws_account_id()

        # Get latest Lambda version and ARN
        lambda_version = get_latest_lambda_version(lambda_name)
        lambda_arn = f"arn:aws:lambda:{aws_region}:{aws_account_id}:function:{lambda_name}:{lambda_version}"
        print(f"Lambda ARN: {lambda_arn}")

        # Check Lambda function status
        check_lambda_status(lambda_name, lambda_version)

        # Update CloudFront distribution
        update_cloudfront_lambda_association(distribution_id, lambda_arn)

        print("Lambda@Edge update process completed successfully.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
