import json
import logging
import os

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from enums.metadata_field_names import DocumentReferenceMetadataFields
from models.nrl_fhir_document_reference import FhirDocumentReference
from models.nrl_sqs_message import NrlAttachment
from pydantic import BaseModel, ValidationError
from services.base.dynamo_service import DynamoDBService
from services.base.nhs_oauth_service import NhsOauthService
from services.base.ssm_service import SSMService
from services.nrl_api_service import NrlApiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProgressForPatient(BaseModel):
    nhs_number: str
    update_completed: bool | str = False


class NRLBatchCreatePointer:
    def __init__(self):
        ssm_service = SSMService()
        auth_service = NhsOauthService(ssm_service)
        self.nrl_service = NrlApiService(ssm_service, auth_service)
        self.dynamo_service = DynamoDBService()
        self.table_name = os.getenv("table_name", "")
        self.progress: list[ProgressForPatient] = []
        self.progress_store = "nrl_batch_update_progress.json"

    def main(self):
        logger.info("Starting batch update script")
        logger.info(f"Table to be updated: {self.table_name}")

        if self.found_previous_progress():
            logger.info("Resuming from previous job")
            self.resume_previous_progress()
        else:
            logger.info("Starting a new job")
            self.list_all_entries()

        try:
            self.create_nrl_pointer()
        except Exception as e:
            logger.error(e)
            raise e

    def found_previous_progress(self) -> bool:
        return os.path.isfile(self.progress_store)

    def resume_previous_progress(self):
        try:
            with open(self.progress_store, "r") as f:
                json_str = json.load(f)
                self.progress = [ProgressForPatient(**item) for item in json_str]
        except FileNotFoundError:
            logger.info("Cannot find a progress file. Will start a new job.")
            self.list_all_entries()
        except ValidationError as e:
            logger.info(e)

    def list_all_entries(self):
        logger.info("Fetching all records from dynamodb table...")

        table = DynamoDBService().get_table(self.table_name)
        results = {}
        columns_to_fetch = DocumentReferenceMetadataFields.NHS_NUMBER.value

        response = table.scan(
            ProjectionExpression=columns_to_fetch,
            FilterExpression=Attr(columns_to_fetch).exists(),
        )
        # handle pagination
        while "LastEvaluatedKey" in response:

            results.update(self.create_progress_dict(response, results))
            response = table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"],
                ProjectionExpression=columns_to_fetch,
                FilterExpression=Attr(columns_to_fetch).exists(),
            )

        results.update(self.create_progress_dict(response, results))
        self.progress = list(results.values())
        logger.info(f"Totally {len(results)} patients found.")

    def create_progress_dict(self, response, results):
        for item in response["Items"]:
            nhs_number = item[DocumentReferenceMetadataFields.NHS_NUMBER.value]
            if nhs_number not in results:
                results[nhs_number] = ProgressForPatient(nhs_number=nhs_number)
        return results

    def create_nrl_pointer(self):
        for patient in self.progress:
            if not patient.update_completed:
                try:
                    # TODO update snomed and attachment, once the API is ready
                    document = (
                        FhirDocumentReference(
                            nhsNumber=patient.nhs_number,
                            snomedCodeDocType="16521000000101",
                            snomedCodeCategory="734163000",
                            custodian=self.nrl_service.end_user_ods_code,
                            attachment=NrlAttachment(
                                url="https://example.org/my-doc.pdf"
                            ),
                        )
                        .build_fhir_dict()
                        .json()
                    )
                    self.nrl_service.create_new_pointer(json.loads(document))
                    patient.update_completed = True

                except ClientError as e:
                    logger.error(e)
                    self.save_progress()
                except Exception as e:
                    patient.update_completed = "Error"
                    logger.error(
                        "Issue creating a pointer for patient number {}, continue to the next patient".format(
                            patient.nhs_number
                        )
                    )
                    logger.error(str(e))
            self.save_progress()

    def save_progress(self):
        with open(self.progress_store, "w") as f:
            progress_list = [patient.model_dump() for patient in self.progress]
            json_str = json.dumps(progress_list)
            f.write(json_str)


if __name__ == "__main__":
    table_name = input("Which table would you like to run the batch script? ")
    os.environ["table_name"] = table_name
    os.environ["NRL_END_USER_ODS_CODE"] = "ndr_ods_code"
    endpoint = input("What is nrl endpoint would you like use? ")
    os.environ["NRL_API_ENDPOINT"] = endpoint
    NRLBatchCreatePointer().main()
