import importlib
import logging
import sys

from services.base.dynamo_service import DynamoDBService


class VersionMigration:
    def __init__(self, table_name: str, dry_run: bool = False):
        self.table_name = table_name
        self.dynamo_service = DynamoDBService()
        self.dry_run = dry_run
        self.logger = logging.getLogger("VersionMigration")

    def main(self):
        self.logger.info("Starting version migration")
        self.logger.info(f"Target table: {self.table_name}")
        self.logger.info(f"Dry run mode: {self.dry_run}")

        try:
            self.run_migration()
        except Exception as e:
            self.logger.error("Migration failed", exc_info=e)
            raise

    def run_migration(self):
        all_entries = self.dynamo_service.scan_whole_table(table_name=self.table_name)
        total_count = len(all_entries)

        for index, entry in enumerate(all_entries, start=1):
            self.logger.info(f"Processing item {index} of {total_count}")
            self.update_item(entry)

        self.logger.info("Migration completed.")

    def update_item(self, item: dict):
        item_id = item.get("id")

        if item.get("version") == 1:
            self.logger.debug(f"Item {item_id} already has version 1, skipping.")
            return

        updated_fields = {"version": 1}

        if self.dry_run:
            self.logger.info(
                f"[Dry Run] Would update item {item_id} with {updated_fields}"
            )
        else:
            self.logger.info(f"Updating item {item_id} with {updated_fields}")
            self.dynamo_service.update_item(
                table_name=self.table_name,
                key_pair={"id": item_id},
                updated_fields=updated_fields,
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
        description="Set 'version' field to 1 in a DynamoDB table",
    )
    parser.add_argument("table_name", help="DynamoDB table name to migrate")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run migration in dry-run mode (no writes)",
    )
    args = parser.parse_args()

    VersionMigration(table_name=args.table_name, dry_run=args.dry_run).main()
