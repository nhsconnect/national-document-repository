import os
import time

import boto3
from utils.audit_logging_setup import LoggingService
from utils.cloudwatch_logs_query import CloudwatchLogsQueryParams
from utils.exceptions import LogsQueryException

logger = LoggingService(__name__)


class CloudwatchService:
    def __init__(self):
        self.logs_client = boto3.client("logs")
        self.workspace = os.environ["WORKSPACE"]
        self.initialised = True

    def query_logs(
        self, query_params: CloudwatchLogsQueryParams, start_time: int, end_time: int
    ) -> list[dict]:
        response = self.logs_client.start_query(
            logGroupName=f"/aws/lambda/{self.workspace}_{query_params.lambda_name}",
            startTime=start_time,
            endTime=end_time,
            queryString=query_params.query_string,
        )
        query_id = response["queryId"]

        raw_query_result = self.poll_query_result(query_id)
        query_result = self.regroup_raw_query_result(raw_query_result)
        return query_result

    def poll_query_result(self, query_id: str, max_retries=20) -> list[list]:
        for _ in range(max_retries):
            response = self.logs_client.get_query_results(queryId=query_id)
            if response["status"] == "Complete":
                return response["results"]
            elif response["status"] in ["Failed", "Cancelled", "Timeout"]:
                self.log_and_raise_error(
                    f"Logs query failed with status: {response['status']}"
                )
            time.sleep(1)

        self.log_and_raise_error(
            f"Failed to get query result within max retries of {max_retries} times"
        )

    @staticmethod
    def regroup_raw_query_result(raw_query_result: list[list[dict]]) -> list[dict]:
        query_result = [
            {column["field"]: column["value"] for column in row}
            for row in raw_query_result
        ]
        return query_result

    @staticmethod
    def log_and_raise_error(error_message: str) -> None:
        logger.error(error_message)
        raise LogsQueryException(error_message)
