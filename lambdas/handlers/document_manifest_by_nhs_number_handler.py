import os
import pathlib
import shutil
import tempfile
import zipfile

import boto3
from enums.metadata_field_names import DynamoDocumentMetadataTableFields
from models.document import Document
from services.dynamo_query_service import DynamoQueryService
from utils.exceptions import InvalidResourceIdException
from utils.lambda_response import ApiGatewayResponse
from utils.nhs_number_validator import validate_id

TABLE_NAME = "test table"
INDEX_NAME = "test index name"


def lambda_handler(event, context):
    # Get and validate the NHS number
    try:
        nhs_number = event["queryStringParameters"]["patientId"]
        validate_id(nhs_number)
    except InvalidResourceIdException:
        return ApiGatewayResponse(
            400, "Invalid NHS number", "GET"
        ).create_api_gateway_response()
    except KeyError:
        return ApiGatewayResponse(
            400, "Please supply an NHS number", "GET"
        ).create_api_gateway_response()

    # Find the locations of the docs for this patient
    documents = find_document_locations(nhs_number)
    if len(documents) == 0:
        return ApiGatewayResponse(
            204, "No documents found for given NHS number", "GET"
        ).create_api_gateway_response()

    # return ApiGatewayResponse(200, "OK", "GET"
    #                           ).create_api_gateway_response()

    ## Lambda console code

    s3 = boto3.client("s3")
    nhs_number = "1234567890"
    bucket_name = "prmd-110-zip-test"

    # Create a temporary directory to store s3 documents for zipping
    temp_dir = tempfile.mkdtemp()

    document_list = [
        Document(
            nhs_number,
            "DNS_Configuration.csv",
            "Clean",
            file_location="s3://prmd-110-zip-test/DNS_Configuration.csv",
        ),
        Document(
            nhs_number,
            "results.csv",
            "Clean",
            file_location="s3://prmd-110-zip-test/results123.csv",
        ),
        Document(
            nhs_number,
            "results.csv",
            "Clean",
            file_location="s3://prmd-110-zip-test/results456.csv",
        ),
    ]

    file_names_to_be_zipped = {}

    # Iterate through the document_list
    for document in document_list:
        file_name = document.file_name

        duplicated_filename = file_name in file_names_to_be_zipped

        if duplicated_filename:
            file_names_to_be_zipped[file_name] += 1
            document.file_name = create_unique_filename(
                file_name, file_names_to_be_zipped[file_name]
            )

        else:
            file_names_to_be_zipped[file_name] = 1

        # Download the S3 object to the temporary directory
        download_path = os.path.join(temp_dir, document.file_name)
        s3.download_file(bucket_name, document.get_file_key(), download_path)

    print(os.listdir(temp_dir))

    # Create a zip file containing all the downloaded files
    temp_output_dir = tempfile.mkdtemp()
    zip_file_name = f"patient-record-{nhs_number}.zip"

    zip_file_path = os.path.join(temp_output_dir, zip_file_name)
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        print(f"Zipping files to {zip_file_path}")
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                print(f"{file_path}")
                arcname = os.path.relpath(file_path, temp_dir)
                print(f"{arcname}")
                zipf.write(file_path, arcname)

    # Upload the zip file to the S3 bucket
    s3.upload_file(zip_file_path, bucket_name, f"{zip_file_name}")

    # # Generate a presigned URL for the zip file
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": f"{zip_file_name}"},
        ExpiresIn=3600,  # Expiration time in seconds
    )

    responseBody = getJsonBody(presigned_url)

    # # Clean up the temporary directories
    shutil.rmtree(temp_dir)
    shutil.rmtree(temp_output_dir)

    return {"statusCode": 200, "body": responseBody}


def getJsonBody(contents):
    return {"result": {"url": contents}}


def create_unique_filename(file_name, duplicates):
    file_name_path = pathlib.Path(file_name)

    return f"{file_name_path.stem}({duplicates}){file_name_path.suffix}"

    # Download all of these documents and zip them
    # Be wary of OutOfMemory errors

    # Upload the new Zip file to S3

    # Return the zip file pre-signed URL


def find_document_locations(nhs_number):
    dynamo_query_service = DynamoQueryService(TABLE_NAME, INDEX_NAME)
    location_query_response = dynamo_query_service(
        "NhsNumber", nhs_number, [DynamoDocumentMetadataTableFields.LOCATION]
    )

    document_locations = []
    for item in location_query_response["Items"]:
        document_locations.append(item["Location"])

    return document_locations


def generate_zip_of_documents(locations: list):
    pass


def upload_to_s3(zip_file):
    pass
