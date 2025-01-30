import json
import logging
import os
import uuid

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from pydantic import BaseModel, ValidationError

from enums.metadata_field_names import DocumentReferenceMetadataFields
from enums.nrl_sqs_upload import NrlActionTypes
from enums.snomed_codes import SnomedCodes
from models.document_reference import DocumentReference
from models.fhir.R4.nrl_fhir_document_reference import Attachment
from models.nrl_sqs_message import NrlSqsMessage
from services.base.dynamo_service import DynamoDBService
from services.base.sqs_service import SQSService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProgressForPatient(BaseModel):
    nhs_number: str
    update_completed: bool | str = False
    document: DocumentReference


class NRLBatchCreatePointer:
    def __init__(self):
        self.dynamo_service = DynamoDBService()
        self.sqs_repository = SQSService()
        self.table_name = os.getenv("table_name", "")
        self.progress: list[ProgressForPatient] = []
        self.progress_store = "nrl_batch_update_progress.json"
        self.nrl_queue_url = os.environ["NRL_SQS_URL"]


    def main(self):
        print("Starting batch update script")
        print(f"Table to be updated: {self.table_name}")

        if self.found_previous_progress():
            print("Resuming from previous job")
            self.resume_previous_progress()
        else:
            print("Starting a new job")
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
            print("Cannot find a progress file. Will start a new job.")
            self.list_all_entries()
        except ValidationError as e:
            print(e)

    def list_all_entries(self):
        print("Fetching all records from dynamodb table...")
        dynamo_service = DynamoDBService()
        results = {}

        response = dynamo_service.scan_table(table_name=self.table_name)
        # handle pagination
        while "LastEvaluatedKey" in response:
            results.update(self.create_progress_dict(response, results))
            response = dynamo_service.scan_table(table_name=self.table_name, exclusive_start_key=response["LastEvaluatedKey"],
                                                 filter_expression=Attr(DocumentReferenceMetadataFields.FILE_NAME.value).begins_with('1of1'))

        results.update(self.create_progress_dict(response, results))
        self.progress = list(results.values())
        print(f"Totally {len(results)} patients found.")

    def create_progress_dict(self, response, results):
        for item in response["Items"]:
            try:
                document = DocumentReference.model_validate(item)
                print(f"Processing patient {document.nhs_number}")
                nhs_number = document.nhs_number
                if nhs_number not in results:
                    results[nhs_number] = ProgressForPatient(nhs_number=nhs_number, document=document)
                else:
                    logger.warning(f"NHS number {nhs_number} has more than one record")
            except ValidationError as e:
                print(e)
                break
        return results

    def create_nrl_pointer(self):
        for patient in self.progress:
            if not patient.update_completed:
                try:
                    document_api_endpoint = (
                            os.environ.get("APIM_API_URL", "")
                            + "/DocumentReference/"
                            + SnomedCodes.LLOYD_GEORGE.value.code
                            + "~"
                            + patient.document.id
                    )
                    doc_details = Attachment(
                        url=document_api_endpoint,
                        contentType="application/pdf",
                    )
                    nrl_sqs_message = NrlSqsMessage(
                        nhs_number=patient.nhs_number,
                        action=NrlActionTypes.CREATE,
                        attachment=doc_details,
                    )
                    self.sqs_repository.send_message_fifo(
                        queue_url=self.nrl_queue_url,
                        message_body=nrl_sqs_message.model_dump_json(),
                        group_id=f"nrl_sqs_{uuid.uuid4()}"
                    )

                    patient.update_completed = True
                    print(f"Create message to {patient.nhs_number}")

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
    endpoint = input("What is api endpoint would you like use?")
    os.environ["APIM_API_URL"] = endpoint
    queue_url = input("What is the queue url?")
    os.environ["NRL_SQS_URL"] = queue_url
    NRLBatchCreatePointer().main()
