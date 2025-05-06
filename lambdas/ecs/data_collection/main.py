import importlib
import logging
import sys

from services.data_collection_service import DataCollectionService
from services.statistical_report_service import StatisticalReportService


def setup_logging_for_local_script():
    importlib.reload(logging)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )


if __name__ == "__main__":
    setup_logging_for_local_script()
    print("Starting data collection process")
    data_collection_service = DataCollectionService()
    data_collection_service.collect_all_data_and_write_to_dynamodb()
    print("Starting to create statistical report")
    statistical_report_service = StatisticalReportService()
    statistical_report_service.make_weekly_summary_and_output_to_bucket()
