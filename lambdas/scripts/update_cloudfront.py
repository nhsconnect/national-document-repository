import logging
import os
import sys
import time

import boto3
from botocore.exceptions import ClientError

# Exit codes
EXIT_SUCCESS = 0
EXIT_ENV_VAR_MISSING = 1
EXIT_LAMBDA_PROPAGATION_FAILED = 2
EXIT_LAMBDA_ASSOC_NOT_FOUND = 3
EXIT_DISTRIBUTION_NOT_FOUND = 4
EXIT_DISTRIBUTION_UPDATE_FAILED = 5
EXIT_CACHE_INVALIDATION_FAILED = 6
EXIT_UNKNOWN_ERROR = 7

# Initialize environment variables
distribution_id = os.getenv("DISTRIBUTION_ID")
aws_region = os.getenv("AWS_REGION")
lambda_arn = os.getenv("LAMBDA_ARN")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def initialize_aws_clients(region):
    session = boto3.Session(region_name=region)
    return {
        "cloudfront": session.client("cloudfront"),
        "lambda": session.client("lambda"),
    }


def validate_environment_variables():
    required_vars = ["DISTRIBUTION_ID", "AWS_REGION", "LAMBDA_ARN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        sys.exit(EXIT_ENV_VAR_MISSING)


def propagate_lambda_update(lambda_client, retry_count=3, initial_delay=5):
    time.sleep(initial_delay)

    for attempt in range(1, retry_count + 1):
        try:
            logger.info(f"Attempt {attempt}: Propagating lambda update...")
            response = lambda_client.get_function_configuration(FunctionName=lambda_arn)
            if (
                response.get("State") == "Active"
                and response.get("LastUpdateStatus") == "Successful"
            ):
                logger.info("Edge Lambda propagated update successfully")
                return True
        except ClientError as e:
            logger.error(
                f"Error checking Lambda function state: {e.response['Error']['Message']}"
            )
            if attempt == retry_count:
                return False

        if attempt < retry_count:
            delay = initial_delay * (2 ** (attempt - 1))  # Exponential backoff
            logger.info(
                f"Edge Lambda has not finished propagating update, retrying in {delay} seconds..."
            )
            time.sleep(delay)

    logger.error("Exceeded retries. Failed to verify Edge Lambda state.")
    return False


def wait_for_distribution_deployment(cloudfront_client, max_attempts=30, delay=60):
    logger.info(
        f"Waiting for CloudFront distribution {distribution_id} to be deployed..."
    )

    for attempt in range(1, max_attempts + 1):
        try:
            response = cloudfront_client.get_distribution(Id=distribution_id)
            status = response["Distribution"]["Status"]

            if status == "Deployed":
                logger.info(
                    f"CloudFront distribution {distribution_id} is now deployed"
                )
                return True

            logger.info(
                f"Attempt {attempt}/{max_attempts}: Distribution status is {status}, waiting {delay} seconds..."
            )
            time.sleep(delay)

        except ClientError as e:
            logger.error(
                f"Error checking distribution status: {e.response['Error']['Message']}"
            )
            return False

    logger.error(
        f"Distribution {distribution_id} did not deploy within the expected timeframe"
    )
    return False


def invalidate_cloudfront_cache(cloudfront_client):
    try:
        invalidation_response = cloudfront_client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                "Paths": {"Quantity": 1, "Items": ["/*"]},
                "CallerReference": str(time.time()),
            },
        )
        invalidation_id = invalidation_response["Invalidation"]["Id"]
        logger.info(f"Cache invalidation started: {invalidation_id}")
        return invalidation_id
    except ClientError as e:
        logger.error(f"Error invalidating cache: {e.response['Error']['Message']}")
        sys.exit(EXIT_CACHE_INVALIDATION_FAILED)


def monitor_invalidation_status(cloudfront_client, invalidation_id):
    logger.info(f"Monitoring invalidation {invalidation_id}...")

    while True:
        try:
            response = cloudfront_client.get_invalidation(
                DistributionId=distribution_id, Id=invalidation_id
            )
            status = response["Invalidation"]["Status"]

            if status == "Completed":
                logger.info(f"Invalidation {invalidation_id} completed successfully")
                break

            logger.info(f"Invalidation status: {status}. Waiting...")
            time.sleep(30)
        except ClientError as e:
            logger.error(
                f"Error monitoring invalidation: {e.response['Error']['Message']}"
            )
            break


def update_cloudfront_lambda_association(cloudfront_client):
    """Update the CloudFront distribution with the new Lambda function version."""
    logger.info(
        f"Updating CloudFront distribution: {distribution_id} with Lambda function ARN: {lambda_arn}"
    )
    try:
        response = cloudfront_client.get_distribution_config(Id=distribution_id)
        distribution_config = response["DistributionConfig"]
        etag = response["ETag"]

        lambda_associations = distribution_config["DefaultCacheBehavior"].get(
            "LambdaFunctionAssociations", {}
        )
        items = lambda_associations.get("Items", [])

        if not items:
            logger.error(
                f"Error for distribution '{distribution_id}'. Lambda associations not found. "
                "Manually clean any duplicated and unused distributions and try again."
            )
            sys.exit(EXIT_LAMBDA_ASSOC_NOT_FOUND)

        updated = False
        for item in items:
            if item["EventType"] in [
                "viewer-request",
                "viewer-response",
                "origin-request",
                "origin-response",
            ]:
                logger.info(
                    f"Updating LambdaFunctionARN for event type {item['EventType']}"
                )
                item["LambdaFunctionARN"] = lambda_arn
                updated = True

        if not updated:
            logger.warning("No Lambda associations were updated")
            return False

        cloudfront_client.update_distribution(
            Id=distribution_id, DistributionConfig=distribution_config, IfMatch=etag
        )
        logger.info(
            f"Updated CloudFront distribution '{distribution_id}' to use Lambda '{lambda_arn}'."
        )
        return True

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "NoSuchDistribution":
            logger.error(
                f"Distribution '{distribution_id}' does not exist. Skipping update."
            )
            sys.exit(EXIT_DISTRIBUTION_NOT_FOUND)
        else:
            logger.error(f"Error updating distribution: {str(e)}")
            sys.exit(EXIT_DISTRIBUTION_UPDATE_FAILED)


def main():
    try:
        validate_environment_variables()

        clients = initialize_aws_clients(aws_region)
        cloudfront_client = clients["cloudfront"]
        lambda_client = clients["lambda"]

        if not propagate_lambda_update(lambda_client, retry_count=3, initial_delay=5):
            logger.error("Failed to propagate Lambda update")
            return EXIT_LAMBDA_PROPAGATION_FAILED

        logger.info(f"Lambda ARN: {lambda_arn}")

        if not update_cloudfront_lambda_association(cloudfront_client):
            logger.error("Failed to update CloudFront Lambda association")
            return EXIT_DISTRIBUTION_UPDATE_FAILED

        if wait_for_distribution_deployment(cloudfront_client):
            invalidation_id = invalidate_cloudfront_cache(cloudfront_client)
            monitor_invalidation_status(cloudfront_client, invalidation_id)
            logger.info("Lambda@Edge update process completed successfully.")
            return EXIT_SUCCESS
        else:
            logger.error("Failed to verify distribution deployment")
            return EXIT_DISTRIBUTION_UPDATE_FAILED

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return EXIT_UNKNOWN_ERROR


if __name__ == "__main__":
    sys.exit(main())
