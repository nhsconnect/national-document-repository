import importlib
import logging
import sys

from services.base.dynamo_service import DynamoDBService


class VersionMigration:
    def __init__(self, environment: str, table_name: str, dry_run: bool = False):
        self.environment = environment
        self.table_name = table_name
        self.dynamo_service = DynamoDBService()
        self.dry_run = dry_run
        self.logger = logging.getLogger("VersionMigration")

        self.target_table = f"{self.environment}_{self.table_name}"
        self.bulk_upload_table = f"{self.environment}_BulkUploadReport"

    def main(self):
        self.logger.info("Starting version migration")
        self.logger.info(f"Target table: {self.target_table}")
        self.logger.info(f"Dry run mode: {self.dry_run}")

        try:
            all_entries = self.dynamo_service.scan_whole_table(
                table_name=self.target_table
            )
            total_count = len(all_entries)

            self.run_version_migration(all_entries=all_entries, total_count=total_count)
            self.run_author_migration(all_entries=all_entries, total_count=total_count)
            self.run_deleted_cleanup_migration(
                all_entries=all_entries, total_count=total_count
            )
            self.run_custodian_migration(
                all_entries=all_entries, total_count=total_count
            )
            self.run_document_snomed_code_type_migration(
                all_entries=all_entries, total_count=total_count
            )
            self.run_status_migration(all_entries=all_entries, total_count=total_count)
            self.run_uploading_migration(
                all_entries=all_entries, total_count=total_count
            )
        except Exception as e:
            self.logger.error("Migration failed", exc_info=e)
            raise

    def process_entries(
        self, label: str, all_entries: list[dict], total_count: int, update_fn
    ):
        self.logger.info(f"Running {label} migration")

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            self.logger.info(
                f"[{label}] Processing item {index} of {total_count} (ID: {item_id})"
            )

            updated_fields = update_fn(entry)
            if not updated_fields:
                self.logger.debug(
                    f"[{label}] Item {item_id} does not require update, skipping."
                )
                continue

            if self.dry_run:
                self.logger.info(
                    f"[Dry Run] Would update item {item_id} with {updated_fields}"
                )
            else:
                self.logger.info(f"Updating item {item_id} with {updated_fields}")
                self.dynamo_service.update_item(
                    table_name=self.target_table,
                    key_pair={"ID": item_id},
                    updated_fields=updated_fields,
                )

        self.logger.info(f"{label} migration completed.")

    def run_version_migration(self, all_entries, total_count):
        self.process_entries(
            "Version",
            all_entries,
            total_count,
            lambda e: {"Version": 1} if e.get("Version") != 1 else None,
        )

    def run_author_migration(self, all_entries, total_count):
        self.logger.info("Running author migration")

        bulk_reports = self.dynamo_service.scan_whole_table(self.bulk_upload_table)
        report_lookup = {
            (r.get("NhsNumber"), r.get("PdsOdsCode")): r.get("UploaderOdsCode")
            for r in bulk_reports
        }

        def author_update(entry):
            key = (entry.get("NhsNumber"), entry.get("CurrentGpOds"))
            author = report_lookup.get(key)
            if not author or entry.get("Author") == author:
                return None
            return {"Author": author}

        self.process_entries("Author", all_entries, total_count, author_update)

    def run_deleted_cleanup_migration(self, all_entries, total_count):
        self.process_entries(
            "Deleted",
            all_entries,
            total_count,
            lambda e: {"Deleted": ""} if e.get("Deleted") == "<empty>" else None,
        )

    def run_custodian_migration(self, all_entries, total_count):
        target_gp_ods = {"REST", "DECE", "SUSP"}
        self.process_entries(
            "Custodian",
            all_entries,
            total_count,
            lambda e: (
                {"Custodian": "X4S4L"}
                if e.get("CurrentGpOds") in target_gp_ods
                else None
            ),
        )

    def run_document_snomed_code_type_migration(self, all_entries, total_count):
        fixed_value = 16521000000101
        self.process_entries(
            "DocumentSnomedCodeType",
            all_entries,
            total_count,
            lambda e: (
                {"DocumentSnomedCodeType": fixed_value}
                if e.get("DocumentSnomedCodeType") != fixed_value
                else None
            ),
        )

    def run_status_migration(self, all_entries, total_count):
        self.process_entries(
            "Status",
            all_entries,
            total_count,
            lambda e: {"Status": "current"} if e.get("Status") != "current" else None,
        )

    def run_uploading_migration(self, all_entries, total_count):
        self.process_entries(
            "Uploading",
            all_entries,
            total_count,
            lambda e: {"Uploading": False} if e.get("Uploading") is not False else None,
        )


def setup_logging():
    importlib.reload(logging)
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


if __name__ == "__main__":
    import argparse

    setup_logging()

    parser = argparse.ArgumentParser(
        prog="dynamodb_migration_20250731.py",
        description="Migrate DynamoDB table columns",
    )
    parser.add_argument("environment", help="Environment prefix for DynamoDB table")
    parser.add_argument("table_name", help="DynamoDB table name to migrate")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run migration in dry-run mode (no writes)",
    )
    args = parser.parse_args()
    VersionMigration(
        environment=args.environment, table_name=args.table_name, dry_run=args.dry_run
    ).main()
