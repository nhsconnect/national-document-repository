import importlib
import logging
import sys
from datetime import datetime

from enums.metadata_field_names import DocumentReferenceMetadataFields
from services.base.dynamo_service import DynamoDBService

Fields = DocumentReferenceMetadataFields


class BatchUpdate:
    def __init__(
        self,
        table_name: str,
    ):
        self.table_name = table_name
        self.dynamo_service = DynamoDBService()
        self.logger = logging.getLogger("Database migration")

    def main(self):
        self.logger.info("Starting batch migration script")
        self.logger.info(f"Table to be updated: {self.table_name}")

        try:
            self.run_update()
        except Exception as e:
            self.logger.error(e)
            raise e

    def run_update(self):
        all_entries = self.list_all_entries()
        total_count = len(all_entries)

        for current_count, entry in enumerate(all_entries):
            self.logger.info(f"Updating record ({current_count} of {total_count})")
            self.update_single_row(entry)

        self.logger.info("Finished updating all records")

    def list_all_entries(self) -> list[dict]:
        self.logger.info("Fetching all records from dynamodb table...")

        scan_results = DynamoDBService().scan_whole_table(table_name=self.table_name)

        return scan_results

    def update_single_row(self, entry: dict):
        doc_ref_id = entry[Fields.ID.value]
        created = entry[Fields.CREATED.value]
        timestamp_now = int(datetime.now().timestamp())

        fields_to_add = [
            Fields.UPLOADED.value,
            Fields.UPLOADING.value,
            Fields.LAST_UPDATED.value,
        ]

        need_update = any(entry.get(field) is None for field in fields_to_add)
        if not need_update:
            return

        uploaded = True
        uploading = False
        last_updated = (
            int(datetime.fromisoformat(created).timestamp())
            if created
            else timestamp_now
        )

        updated_fields = {
            Fields.UPLOADED.value: uploaded,
            Fields.UPLOADING.value: uploading,
            Fields.LAST_UPDATED.value: last_updated,
        }
        self.dynamo_service.update_item(
            table_name=self.table_name,
            key=doc_ref_id,
            updated_fields=updated_fields,
        )


def setup_logging_for_local_script():
    importlib.reload(logging)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )


if __name__ == "__main__":
    import argparse

    setup_logging_for_local_script()

    parser = argparse.ArgumentParser(
        prog="dynamodb_migration_20240618.py",
        description="A utility script to update the missing columns for in a dynamoDB doc reference table",
    )
    parser.add_argument("table_name", type=str, help="The name of dynamodb table")
    args = parser.parse_args()

    BatchUpdate(table_name=args.table_name).main()
