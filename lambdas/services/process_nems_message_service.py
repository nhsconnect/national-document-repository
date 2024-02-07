import os
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from botocore.exceptions import ClientError
from enums.fhir_resource_message_types import FHIR_RESOURCE_MESSAGE_TYPES
from enums.fhir_resource_types import FHIR_RESOURCE_TYPES
from enums.nems_error_types import NEMS_ERROR_TYPES
from fhir.resources.STU3.bundle import Bundle
from pydantic import ValidationError as PydanticValidationError
from pydantic.v1.error_wrappers import ValidationError as PydanticValidationErrorWrapper
from services.document_service import DocumentService
from services.ods_api_service import OdsApiService
from utils.audit_logging_setup import LoggingService
from utils.exceptions import (
    FhirResourceNotFound,
    InvalidResourceIdException,
    OdsErrorException,
    OrganisationNotFoundException,
)
from utils.fhir_bundle_parser import map_bundle_entries_to_dict
from utils.request_context import request_context
from utils.utilities import validate_id

logger = LoggingService(__name__)


class ProcessNemsMessageService:
    def __init__(self):
        self.ods_api_service = OdsApiService()
        self.document_service = DocumentService()
        self.table = os.environ["LLOYD_GEORGE_DYNAMODB_NAME"]

    def process_messages_from_event(self, records: list):
        batch_item_failures = []

        for message in records:
            response = self.handle_message(message)
            logger.info(response)
            if response is not None:
                batch_item_failures.append({"itemIdentifier": message["messageId"]})

        return batch_item_failures

    def handle_message(self, message: dict):
        try:
            mesh_message_id = "No mesh id identified"
            mesh_attributes = message["messageAttributes"]
            mesh_message_id = mesh_attributes.get("meshMessageId")
            nems_message = message["body"]

            ElementTree.fromstring(nems_message)
            bundle = Bundle.parse_raw(nems_message, content_type="text/xml")
            mapped_bundle = map_bundle_entries_to_dict(bundle)
            message_header = mapped_bundle.get(
                FHIR_RESOURCE_TYPES.MessageHeader.value, None
            )

            if message_header is None:
                raise FhirResourceNotFound(
                    {"resourceType": FHIR_RESOURCE_TYPES.MessageHeader, "details": ""}
                )

            # We do not process messages that are not of an expected type
            if (
                message_header[0].resource.event.code
                == FHIR_RESOURCE_MESSAGE_TYPES.ChangeOfGP
            ):
                return self.handle_change_of_gp_message(mapped_bundle)
            else:
                logger.info(
                    f"The NEMs message is not of a type that we support: {mesh_message_id}"
                )

        except (PydanticValidationError, PydanticValidationErrorWrapper):
            logger.error(
                f"Validation error - Invalid NEMS message, message id: {mesh_message_id}, ignoring message"
            )
            return NEMS_ERROR_TYPES.Validation
        except SyntaxError as e:
            logger.error(
                f"Syntax error: {e}, message id: {mesh_message_id}, ignoring message"
            )
            return NEMS_ERROR_TYPES.Validation
        except KeyError:
            logger.error(
                f"Message body is not a Bundle, message id: {mesh_message_id}, ignoring message"
            )
            return NEMS_ERROR_TYPES.Validation
        except ParseError:
            logger.error(
                f"Parse error - Invalid NEMS message, message id: {mesh_message_id}, ignoring message"
            )
            return NEMS_ERROR_TYPES.Validation
        except InvalidResourceIdException:
            logger.error(
                f"Invalid nhs number, message id: {mesh_message_id}, ignoring message"
            )
            return NEMS_ERROR_TYPES.Data
        except OdsErrorException:
            return NEMS_ERROR_TYPES.Data
        except OrganisationNotFoundException:
            logger.error(
                f"ODS code for new GPP is invalid, message id: {mesh_message_id}"
            )
            return NEMS_ERROR_TYPES.Data
        except FhirResourceNotFound as e:
            args = e.args[0]
            resource_type = args["resourceType"]
            logger.error(
                f"Expected FHIR entry is missing of type: {resource_type.value}"
            )
            return NEMS_ERROR_TYPES.Data
        except ClientError as e:
            logger.error(f"Error with one of our services, {e}")
            logger.error(
                f"Returning the message back to the queue, message id: {mesh_message_id}"
            )
            return NEMS_ERROR_TYPES.Transient

    def handle_change_of_gp_message(self, mapped_bundle: dict):
        patient_entries = mapped_bundle.get(FHIR_RESOURCE_TYPES.Patient.value)

        if patient_entries is None:
            raise FhirResourceNotFound(
                {"resourceType": FHIR_RESOURCE_TYPES.Patient, "details": ""}
            )

        patient = patient_entries[0].resource
        patient_active_gp = patient.generalPractitioner[0].reference
        patient_nhs_number = patient.identifier[0].value
        validate_id(patient_nhs_number)

        organisation_entries = mapped_bundle.get(FHIR_RESOURCE_TYPES.Organisation.value)
        if organisation_entries is None:
            raise FhirResourceNotFound(
                {"resourceType": FHIR_RESOURCE_TYPES.Organisation, "details": ""}
            )

        active_gp_resource = None
        for organisation in organisation_entries:
            if organisation.fullUrl == patient_active_gp:
                active_gp_resource = organisation.resource

        if not active_gp_resource:
            raise FhirResourceNotFound(
                {
                    "resourceType": FHIR_RESOURCE_TYPES.Organisation,
                    "details": "Active GP could not be identified",
                }
            )

        # We use NHS number to look up where the ods needs to be updated,
        # therefore we're not worried about getting the previous gp resource
        active_gp_ods = active_gp_resource.identifier[0].value

        request_context.patient_nhs_no = patient_nhs_number
        self.validate_nems_details(active_gp_ods)
        self.update_LG_table_with_current_GP(patient_nhs_number, active_gp_ods)
        return

    def validate_nems_details(self, new_ods_code: str):
        self.ods_api_service.fetch_organisation_data(new_ods_code)

    def update_LG_table_with_current_GP(self, nhs_number: str, new_ods_code: str):
        logger.info("getting record from DB")
        documents = self.document_service.fetch_documents_from_table(
            nhs_number, self.table
        )
        if documents:
            logger.info(f"doc: {documents}")
            self.document_service.update_documents(
                self.table, documents, {"CurrentGpOds": new_ods_code}
            )
        else:
            logger.info(
                f"no records were found for the following nhs number: {nhs_number}, ignoring message"
            )
