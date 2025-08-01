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
        except Exception as e:
            self.logger.error("Migration failed", exc_info=e)
            raise

    def run_version_migration(self, all_entries: list[dict], total_count: int) -> None:
        self.logger.info("Running version migration")

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            current_version = entry.get("Version")
            self.logger.info(
                f"[Version] Processing item {index} of {total_count} (ID: {item_id})"
            )

            if current_version == 1:
                self.logger.debug(
                    f"[Version] Item {item_id} already at version 1, skipping."
                )
                continue

            updated_fields = {"Version": 1}

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

        self.logger.info("Version migration completed.")

    def run_author_migration(self, all_entries: list[dict], total_count: int) -> None:
        self.logger.info("Running author migration")

        # Fetch BulkUploadReport table once, build a lookup dict keyed by (NhsNumber, PdsOdsCode)
        bulk_reports = self.dynamo_service.scan_whole_table(
            table_name=self.bulk_upload_table
        )
        report_lookup = {}
        for r in bulk_reports:
            key = (r.get("NhsNumber"), r.get("PdsOdsCode"))
            if key not in report_lookup:
                report_lookup[key] = r.get("UploaderOdsCode")

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            nhs_number = entry.get("NhsNumber")
            current_gp_ods = entry.get("CurrentGpOds")
            self.logger.info(
                f"[Author] Processing item {index} of {total_count} (ID: {item_id})"
            )

            # Lookup matching author
            author = report_lookup.get((nhs_number, current_gp_ods))
            if not author:
                self.logger.debug(
                    f"[Author] No matching BulkUploadReport for item {item_id}, skipping."
                )
                continue

            if entry.get("Author") == author:
                self.logger.debug(
                    f"[Author] Item {item_id} already has Author '{author}', skipping."
                )
                continue

            updated_fields = {"Author": author}

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

        self.logger.info("Author migration completed.")

    def run_deleted_cleanup_migration(
        self, all_entries: list[dict], total_count: int
    ) -> None:
        self.logger.info("Running deleted field cleanup migration")

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            deleted_value = entry.get("Deleted")

            self.logger.info(
                f"[Deleted] Processing item {index} of {total_count} (ID: {item_id})"
            )

            if deleted_value != "<empty>":
                self.logger.debug(
                    f"[Deleted] Item {item_id} has Deleted = '{deleted_value}', skipping."
                )
                continue

            updated_fields = {"Deleted": ""}

            if self.dry_run:
                self.logger.info(
                    f"[Dry Run] Would update item {item_id} to clear Deleted field"
                )
            else:
                self.logger.info(f"Updating item {item_id} to clear Deleted field")
                self.dynamo_service.update_item(
                    table_name=self.target_table,
                    key_pair={"ID": item_id},
                    updated_fields=updated_fields,
                )

        self.logger.info("Deleted field cleanup completed.")

    def run_custodian_migration(self, all_entries, total_count):
        self.logger.info("Running custodian cleanup migration")

        target_gp_ods_values = {"REST", "DECE", "SUSP"}

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            current_gp_ods = entry.get("CurrentGpOds")

            self.logger.info(
                f"[Custodian] Processing item {index} of {total_count} (ID: {item_id})"
            )

            if current_gp_ods not in target_gp_ods_values:
                self.logger.debug(
                    f"[Custodian] Item {item_id} has CurrentGpOds = '{current_gp_ods}', skipping."
                )
                continue

            updated_fields = {"Custodian": "X4S4L"}

            if self.dry_run:
                self.logger.info(
                    f"[Dry Run] Would update item {item_id} to set Custodian = 'X4S4L'"
                )
            else:
                self.logger.info(f"Updating item {item_id} to set Custodian = 'X4S4L'")
                self.dynamo_service.update_item(
                    table_name=self.target_table,
                    key_pair={"ID": item_id},
                    updated_fields=updated_fields,
                )

        self.logger.info("Custodian cleanup completed.")

    def run_document_snomed_code_type_migration(self, all_entries, total_count):
        self.logger.info("Running DocumentSnomedCodeType migration")

        fixed_value = 16521000000101

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            current_value = entry.get("DocumentSnomedCodeType")
            self.logger.info(
                f"[DocumentSnomedCodeType] Processing item {index} of {total_count} (ID: {item_id})"
            )

            if current_value == fixed_value:
                self.logger.debug(
                    f"[DocumentSnomedCodeType] Item {item_id} already has value {fixed_value}, skipping."
                )
                continue
            updated_fields = {"DocumentSnomedCodeType": fixed_value}

            if self.dry_run:
                self.logger.info(
                    f"[Dry Run] Would update item {item_id} to set DocumentSnomedCodeType = {fixed_value}"
                )
            else:
                self.logger.info(
                    f"Updating item {item_id} to set DocumentSnomedCodeType = {fixed_value}"
                )
                self.dynamo_service.update_item(
                    table_name=self.target_table,
                    key_pair={"ID": item_id},
                    updated_fields=updated_fields,
                )

        self.logger.info("DocumentSnomedCodeType migration completed.")

    def run_status_migration(self, all_entries, total_count):
        self.logger.info("Running Status migration")

        target_value = "current"

        for index, entry in enumerate(all_entries, start=1):
            item_id = entry.get("ID")
            current_status = entry.get("Status")

            self.logger.info(
                f"[Status] Processing item {index} of {total_count} (ID: {item_id})"
            )

            if current_status == target_value:
                self.logger.debug(
                    f"[Status] Item {item_id} already has value '{target_value}', skipping."
                )
                continue

            updated_fields = {"Status": target_value}

            if self.dry_run:
                self.logger.info(
                    f"[Dry Run] Would update item {item_id} to set Status = '{target_value}'"
                )
            else:
                self.logger.info(
                    f"Updating item {item_id} to set Status = '{target_value}'"
                )
                self.dynamo_service.update_item(
                    table_name=self.target_table,
                    key_pair={"ID": item_id},
                    updated_fields=updated_fields,
                )

        self.logger.info("Status migration completed.")


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
