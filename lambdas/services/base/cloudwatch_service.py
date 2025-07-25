import os
import time
from datetime import datetime, timezone

import boto3
from utils.audit_logging_setup import LoggingService
from utils.cloudwatch_logs_query import CloudwatchLogsQueryParams
from utils.exceptions import LogsQueryException

logger = LoggingService(__name__)


class CloudwatchService:
    def __init__(self):
        self.logs_client = boto3.client("logs")
        self.cloudwatch_client = boto3.client("cloudwatch")
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

    def publish_metric(
        self,
        metric_name: str,
        value: float,
        namespace: str,
        dimensions: list[dict] = None,
        unit: str = "Count",
        timestamp: float = None,
    ):
        """Publish a custom CloudWatch metric."""
        if dimensions is None:
            dimensions = []

        if timestamp is None:
            timestamp = time.time()

        try:
            self.cloudwatch_client.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Dimensions": dimensions,
                        "Value": value,
                        "Unit": unit,
                        "Timestamp": datetime.fromtimestamp(timestamp, tz=timezone.utc),
                        "StorageResolution": 1,
                    }
                ],
            )
            logger.info(
                f"[METRIC] Published '{metric_name}' = {value} | ODSCode = {dimensions} "
                f"| Time = {datetime.fromtimestamp(timestamp).isoformat()}"
            )
        except Exception as e:
            logger.error(f"Failed to publish metric {metric_name}: {e}")

    def get_metric_data_points(self, metric_name: str, namespace: str) -> list[dict]:
        single_day_time = 86400
        end_time = datetime.now(timezone.utc)
        start_time = datetime.fromtimestamp(
            end_time.timestamp() - 14 * single_day_time, tz=timezone.utc
        )

        paginator = self.cloudwatch_client.get_paginator("get_metric_data")
        response_iterator = paginator.paginate(
            MetricDataQueries=[
                {
                    "Id": "metricdata",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": namespace,
                            "MetricName": metric_name,
                        },
                        "Period": single_day_time,
                        "Stat": "Sum",
                    },
                    "ReturnData": True,
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
        )

        results = []
        for response in response_iterator:
            for result in response.get("MetricDataResults", []):
                for timestamp, value in zip(result["Timestamps"], result["Values"]):
                    results.append(
                        {
                            "Timestamp": timestamp,
                            "Value": value,
                        }
                    )

        return results

    def list_dimension_values(
        self, metric_name: str, namespace: str, dimension_name: str
    ) -> list[str]:
        paginator = self.cloudwatch_client.get_paginator("list_metrics")
        dimension_values = set()

        for page in paginator.paginate(Namespace=namespace, MetricName=metric_name):
            for metric in page.get("Metrics", []):
                for dim in metric.get("Dimensions", []):
                    if dim["Name"] == dimension_name:
                        dimension_values.add(dim["Value"])

        return list(dimension_values)

    def get_metric_data_by_dimension(
        self,
        metric_name: str,
        namespace: str,
        dimension: dict = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> list[dict]:
        single_day_time = 86400  # 1 day in seconds

        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            # default to 14 days ago
            start_time = datetime.fromtimestamp(
                end_time.timestamp() - 14 * single_day_time, tz=timezone.utc
            )

        dimensions = [dimension] if dimension else []

        paginator = self.cloudwatch_client.get_paginator("get_metric_data")
        response_iterator = paginator.paginate(
            MetricDataQueries=[
                {
                    "Id": "metricdata",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": namespace,
                            "MetricName": metric_name,
                            "Dimensions": dimensions,
                        },
                        "Period": single_day_time,
                        "Stat": "Sum",
                    },
                    "ReturnData": True,
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
        )

        results = []
        for response in response_iterator:
            for result in response.get("MetricDataResults", []):
                for timestamp, value in zip(result["Timestamps"], result["Values"]):
                    results.append(
                        {
                            "Timestamp": timestamp,
                            "Value": value,
                        }
                    )

        return results

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
