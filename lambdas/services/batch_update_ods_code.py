import os.path
import time
from typing import Dict

from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.pds_models import Patient
from pydantic import BaseModel, TypeAdapter
from services.base.dynamo_service import DynamoDBService
from services.base.ssm_service import SSMService
from services.pds_api_service import PdsApiService
from utils.audit_logging_setup import LoggingService

Fields = DocumentReferenceMetadataFields

logger = LoggingService(__name__)


class ProgressForPatient(BaseModel):
    nhs_number: str
    doc_ref_ids: list[str]
    prev_ods_code: str = ""
    new_ods_code: str = ""
    update_completed: bool = False


class BatchUpdate:
    def __init__(
        self,
        table_name: str,
        progress_store_file_path: str = "batch_update_progress.json",
    ):
        self.progress_store = progress_store_file_path
        self.table_name = table_name
        self.pds_service = PdsApiService(SSMService())
        self.dynamo_service = DynamoDBService()
        self.progress: Dict[str, ProgressForPatient] = {}

    def main(self):
        logger.info("Starting batch update script")
        logger.info(f"Table to be updated: {self.table_name}")

        if self.found_previous_progress():
            logger.info("Resuming from previous job")
            self.resume_previous_progress()
        else:
            logger.info("Starting a new job")
            self.initialise_new_job()

        try:
            self.run_update()
        except Exception as e:
            logger.error(e)
            raise e

    def run_update(self):
        if len(self.progress) == 0:
            logger.info(
                f'No patient found in local progress file. Please try removing the local progress file: "{self.progress}"'
            )
            exit()

        patients_to_be_updated = [
            nhs_number
            for [nhs_number, status] in self.progress.items()
            if not status.update_completed
        ]
        if not patients_to_be_updated:
            logger.info(
                "Already updated the ODS codes for all patients in previous run."
            )
            exit()

        total_count = len(self.progress.items())
        count_of_completed = total_count - len(patients_to_be_updated)
        for [current_count, nhs_number] in enumerate(
            patients_to_be_updated, start=count_of_completed + 1
        ):
            logger.info(
                f"Updating record for NHS number {nhs_number} ({current_count} of {total_count})"
            )
            self.update_patient_ods(nhs_number)

        logger.info("Finished updating all patient's ODS codes")

    def update_patient_ods(self, nhs_number: str):
        updated_gp_ods = self.get_updated_gp_ods(nhs_number)
        if updated_gp_ods == self.progress[nhs_number].prev_ods_code:
            logger.info(f"No change in GP for patient: {nhs_number}")
        else:
            documents_to_update = self.progress[nhs_number].doc_ref_ids
            updated_fields = {Fields.CURRENT_GP_ODS.value: updated_gp_ods}

            for doc_ref_id in documents_to_update:
                self.dynamo_service.update_item(
                    table_name=self.table_name,
                    key=doc_ref_id,
                    updated_fields=updated_fields,
                )

            logger.info(f"Updated ODS code for patient: {nhs_number}")

        self.progress[nhs_number].new_ods_code = updated_gp_ods
        self.progress[nhs_number].update_completed = True
        self.save_progress()

    def get_updated_gp_ods(self, nhs_number: str) -> str:
        time.sleep(0.2)  # buffer to avoid over stretching PDS API
        logger.debug("Getting the latest ODS code from PDS...")

        pds_response = self.pds_service.pds_request(
            nhs_number=nhs_number, retry_on_expired=True
        )
        pds_response.raise_for_status()

        pds_response_json = pds_response.json()

        patient = Patient.model_validate(pds_response_json)

        ods_code = patient.get_active_ods_code_for_gp()

        deceased = bool(pds_response_json.get("deceasedDateTime"))
        if deceased:
            return "DECE"

        if not ods_code:
            return "SUSP"

        return ods_code

    def initialise_new_job(self):
        all_entries = self.list_all_entries()
        if len(all_entries) == 0:
            logger.info(
                f"No records was found in table {self.table_name}. Please check the table name."
            )
            exit()

        self.progress = self.build_progress_dict(all_entries)

    def resume_previous_progress(self):
        try:
            with open(self.progress_store, "r") as f:
                json_str = f.read()
                self.progress = TypeAdapter(
                    Dict[str, ProgressForPatient]
                ).validate_json(json_str)
        except FileNotFoundError:
            logger.info("Cannot find a progress file. Will start a new job.")
            self.initialise_new_job()

    def found_previous_progress(self) -> bool:
        return os.path.isfile(self.progress_store)

    def save_progress(self):
        with open(self.progress_store, "wb") as f:
            json_str = TypeAdapter(Dict[str, ProgressForPatient]).dump_json(
                self.progress
            )
            return f.write(json_str)

    def list_all_entries(self) -> list[dict]:
        logger.info("Fetching all records from dynamodb table...")

        table = DynamoDBService().get_table(self.table_name)
        results = []
        columns_to_fetch = ",".join(
            enum.value for enum in [Fields.ID, Fields.NHS_NUMBER, Fields.CURRENT_GP_ODS]
        )

        response = table.scan(ProjectionExpression=columns_to_fetch)

        # handle pagination
        while "LastEvaluatedKey" in response:
            results += response["Items"]
            response = table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"],
                ProjectionExpression=columns_to_fetch,
            )

        results += response["Items"]

        logger.info(f"Downloaded {len(results)} records from table")

        return results

    def build_progress_dict(self, dynamodb_records: list[dict]) -> dict:
        logger.info("Grouping the records according to NHS number...")

        progress_dict = {}
        for entry in dynamodb_records:
            nhs_number = entry[Fields.NHS_NUMBER.value]
            doc_ref_id = entry[Fields.ID.value]
            ods_code = entry.get(Fields.CURRENT_GP_ODS.value, "")

            if nhs_number not in progress_dict:
                progress_dict[nhs_number] = ProgressForPatient(
                    nhs_number=nhs_number,
                    doc_ref_ids=[doc_ref_id],
                    prev_ods_code=ods_code,
                )
            else:
                progress_dict[nhs_number].doc_ref_ids.append(doc_ref_id)
                pds_code_at_current_row = ods_code
                if progress_dict[nhs_number].prev_ods_code != pds_code_at_current_row:
                    progress_dict[nhs_number].prev_ods_code = (
                        "[multiple ods codes in records]"
                    )

        logger.info(f"Totally {len(progress_dict)} patients found in record.")
        return progress_dict
