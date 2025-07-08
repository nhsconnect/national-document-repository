# NHS National Document Repository (NDR) API Specification

## Overview

This document provides a comprehensive specification of all Lambda functions and API endpoints in the NHS National Document Repository system. The NDR is a cloud-based service for managing patient documents within the NHS.

## Authentication

Most endpoints require custom authorization via the `repo_authoriser` Lambda function. Some endpoints use API keys for machine-to-machine communication.

---

## API Endpoints

### - Patient Search

**Handler**: [`search_patient_details_handler.lambda_handler`](./national-document-repository/lambdas/handlers/search_patient_details_handler.py)

**Endpoint**: `/SearchPatient`  
**Method**: `GET`  
**Authorization**: CIS2 Authenticatied Session  
**Query Parameters**:

- `patientId` - NHS Number of the patient

**Description**: Searches for patient details in PDS (Personal Demographics Service)
This lambda accept a `patientId` (NHS number) and search for
patient's details in the PDS API.

If successful, the lambda will return status code 200 with patient details as the below example:

```json
{
  "givenName": ["Jane"],
  "familyName": "Smith",
  "birthDate": "2010-10-22",
  "postalCode": "LS1 6AE",
  "nhsNumber": "9000000009",
  "superseded": false,
  "restricted": false
}
```

**Response**: Patient details including name, date of birth, and GP practice information

---

### - Document Reference Search

**Handler**: [`document_reference_search_handler.lambda_handler`](./national-document-repository/lambdas/handlers/document_reference_search_handler.py)

**Endpoint**: `/SearchDocumentReferences`  
**Method**: `GET`  
**Authorization**: CIS2 Authenticatied Session  
**Query Parameters**:

- `patientId` - NHS Number of the patient

**Description**: Retrieves all document references for a specific patient
This lambda is used to search DynamoDB for the documents uploaded against a patient's NHS number.

It only returns what is required to display on the frontend page, notably any file names, times the files were
originally uploaded and the result of the virus scan.

**Response**: Array of document references with metadata

#### Example inputs

Testing in AWS on the lambda directly:

```json
{
  "queryStringParameters": {
    "patientId": "9449305552"
  }
}
```

Testing through API Gateway:

Require input value:

- queryStringParameters: `patientId` (string, 10 digits, nhs number)

```
patientId=9449305552
```

Hitting URL directly:

```
https://{url}/SearchDocumentReferences?patientId=9449305552
```

#### Possible outputs

Expected response:

- If document records were found, respond with 200 and a response body in this format:

```json
[
  {
    "FileName": "nhs1-3669038588 (1).png",
    "Created": "2023-09-05T08:34:15.662364Z"
  },
  {
    "FileName": "nhs1-test-lloyd-george (1).png",
    "Created": "2023-09-05T08:34:15.662364Z"
  }
]
```

- If documents were not found, respond with 204 and a empty response body.

- If invalid `patientId` was given, respond with 400 and `Invalid NHS number` as response body.

- If `patientId` was not given, respond with 400 and `Please supply an NHS number` as response body.

Success:

```json
{
  "isBase64Encoded": false,
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET"
  },
  "body": "[{\"FileName\": \"nhs1-3669038588 (1).png\", \"Created\": \"2023-09-05T08:34:15.662364Z\"}, {\"FileName\": \"nhs1-test-lloyd-george (1).png\", \"Created\": \"2023-09-05T08:34:15.662364Z\", \"VirusScannerResult\": \"Clean\", \"CurrentGpOds\": \"Y12345\"}]"
}
```

If there is no data for a given NHS number:

```json
{
  "isBase64Encoded": false,
  "statusCode": 204,
  "headers": {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET"
  },
  "body": ""
}
```

If the NHS number is not valid:

```json
{
  "isBase64Encoded": false,
  "statusCode": 400,
  "headers": {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET"
  },
  "body": "Invalid NHS number"
}
```

If an NHS number was not supplied correctly to the funtion:

```json
{
  "isBase64Encoded": false,
  "statusCode": 400,
  "headers": {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET"
  },
  "body": "Please supply an NHS number"
}
```

If an error occurred when querying DynamoDB:

```json
{
  "isBase64Encoded": false,
  "statusCode": 500,
  "headers": {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET"
  },
  "body": "Unrecognised response when searching for available documents"
}
```

or...

```json
{
  "isBase64Encoded": false,
  "statusCode": 500,
  "headers": {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET"
  },
  "body": "An error occurred searching for available documents"
}
```

---

### - Create Document Reference

**Handler**: [`create_document_reference_handler.lambda_handler`](./national-document-repository/lambdas/handlers/create_document_reference_handler.py)

**Endpoint**: `/DocumentReference`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session  
**Query Parameters**:

- `patientId` - NHS Number of the patient

**Request Body**:

```json
{
  "subject": {
    "identifier": {
      "value": "NHS_NUMBER"
    }
  },
  "content": [
    {
      "attachment": [
        {
          "fileName": "document.pdf",
          "contentType": "application/pdf"
        }
      ]
    }
  ]
}
```

**Description**: Creates document references and generates presigned URLs for document upload

**Response**: Array of presigned URLs for document upload

---

### - Delete Document Reference

**Handler**: [`delete_document_reference_handler.lambda_handler`](./national-document-repository/lambdas/handlers/delete_document_reference_handler.py)

**Endpoint**: `/DocumentDelete`  
**Method**: `DELETE`  
**Authorization**: CIS2 Authenticatied Session  
**Query Parameters**:

- `patientId` - NHS Number of the patient
- `docType` - Type of document (ARF, LG)

**Description**: Deletes document references and associated files

---

### - Lloyd George Record Stitch

**Handler**: [`lloyd_george_record_stitch_handler.lambda_handler`](./national-document-repository/lambdas/handlers/lloyd_george_record_stitch_handler.py)

**Endpoint**: `/LloydGeorgeStitch`  
**Methods**: `GET`, `POST`  
**Authorization**: CIS2 Authenticatied Session

**GET**: Retrieves stitching status  
**POST**: Initiates Lloyd George record stitching process

**Description**: Manages the stitching of Lloyd George records into a single PDF

---

### - Document Manifest

**Handler**: [`document_manifest_job_handler.lambda_handler`](./national-document-repository/lambdas/handlers/document_manifest_job_handler.py)

**Endpoint**: `/DocumentManifest`  
**Methods**: `GET`, `POST`  
**Authorization**: CIS2 Authenticatied Session

**GET**: Retrieves manifest job status  
**POST**: Creates a new manifest job

**Description**: Manages document manifest generation for bulk operations
The manifest lambda expects two query string parameters called patientId and docType.

**patientId** is to be supplied as a String, and should conform to standard NHS Number format

**docType** is a String and expects a single or comma-seperated list of types of document you're searching for.
It can be set to the following values:

For just Lloyd George docs "LG"

For just ARF docs "ARF"

For all docs "LG,ARF"

If the parameter is not supplied, the values contain something unspecified, or it is an empty String, a 400 error will be returned

---

### - Feature Flags

**Handler**: [`feature_flags_handler.lambda_handler`](./national-document-repository/lambdas/handlers/feature_flags_handler.py)

**Endpoint**: `/FeatureFlags`  
**Method**: `GET`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Retrieves feature flag configurations for the application

**Response**: JSON object with feature flag states

---

### - Upload State Update

**Handler**: [`update_upload_state_handler.lambda_handler`](./national-document-repository/lambdas/handlers/update_upload_state_handler.py)

**Endpoint**: `/UploadState`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Updates the state of document uploads

---

### - Upload Confirmation

**Handler**: [`upload_confirm_result_handler.lambda_handler`](./national-document-repository/lambdas/handlers/upload_confirm_result_handler.py)

**Endpoint**: `/UploadConfirm`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Confirms successful document upload

---

### - Virus Scan Result

**Handler**: [`virus_scan_result_handler.lambda_handler`](./national-document-repository/lambdas/handlers/virus_scan_result_handler.py)

**Endpoint**: `/VirusScan`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Receives and processes virus scan results for uploaded documents

---

### - Access Audit

**Handler**: [`access_audit_handler.lambda_handler`](./national-document-repository/lambdas/handlers/access_audit_handler.py)

**Endpoint**: `/AccessAudit`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Records access audit events for compliance

---

### - Feedback

**Handler**: [`send_feedback_handler.lambda_handler`](./national-document-repository/lambdas/handlers/send_feedback_handler.py)

**Endpoint**: `/Feedback`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Submits user feedback

---

### - ODS Report

**Handler**: [`get_report_by_ods_handler.lambda_handler`](./national-document-repository/lambdas/handlers/get_report_by_ods_handler.py)

**Endpoint**: `/OdsReport`  
**Method**: `GET`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Generates reports by ODS (Organisation Data Service) code

---

### - Token Request

**Handler**: [`token_handler.lambda_handler`](./national-document-repository/lambdas/handlers/token_handler.py)

**Endpoint**: `/TokenRequest`  
**Method**: `GET`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Manages authentication tokens

---

### - Logout

**Handler**: [`logout_handler.lambda_handler`](./national-document-repository/lambdas/handlers/logout_handler.py)

**Endpoint**: `/Logout`  
**Method**: `GET`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Handles user logout

---

### - Back Channel Logout

**Handler**: [`back_channel_logout_handler.lambda_handler`](./national-document-repository/lambdas/handlers/back_channel_logout_handler.py)

**Endpoint**: `/BackChannelLogout`  
**Method**: `POST`  
**Authorization**: CIS2 Authenticatied Session

**Description**: Handles OAuth2 back-channel logout

---

<br>

## Non-API Gateway Lambda Functions

### - Authoriser

**Handler**: [`authoriser_handler.lambda_handler`](./national-document-repository/lambdas/handlers/authoriser_handler.py)

**Type**: API Gateway Custom Authorizer  
**Description**: Validates authentication tokens for API requests

### - Edge Presign

**Handler**: [`edge_presign_handler.lambda_handler`](./national-document-repository/lambdas/handlers/edge_presign_handler.py)

**Type**: CloudFront Edge Function  
**Description**: Generates presigned URLs at the edge for document access

### - Bulk Upload

**Handler**: [`bulk_upload_handler.lambda_handler`](./national-document-repository/lambdas/handlers/bulk_upload_handler.py)

**Type**: SQS-triggered  
**Description**: Processes bulk document uploads

### - Bulk Upload Metadata

**Handler**: [`bulk_upload_metadata_handler.lambda_handler`](./national-document-repository/lambdas/handlers/bulk_upload_metadata_handler.py)

**Type**: Event-driven  
**Description**: Processes metadata for bulk uploads

### - Bulk Upload Metadata Preprocessor

**Handler**: [`bulk_upload_metadata_preprocessor_handler.lambda_handler`](./national-document-repository/lambdas/handlers/bulk_upload_metadata_preprocessor_handler.py)

**Type**: Event-driven  
**Description**: Preprocesses bulk upload metadata

### - Bulk Upload Report

**Handler**: [`bulk_upload_report_handler.lambda_handler`](./national-document-repository/lambdas/handlers/bulk_upload_report_handler.py)

**Type**: Scheduled/Event-driven  
**Description**: Generates reports for bulk upload operations

### - Data Collection

**Handler**: [`data_collection_handler.lambda_handler`](./national-document-repository/lambdas/handlers/data_collection_handler.py)

**Type**: Scheduled (runs in ECS)  
**Description**: Collects system metrics and usage data

### - Delete Document Object

**Handler**: [`delete_document_object_handler.lambda_handler`](./national-document-repository/lambdas/handlers/delete_document_object_handler.py)

**Type**: SQS-triggered  
**Description**: Handles asynchronous deletion of document objects from S3

### - Generate Document Manifest

**Handler**: [`generate_document_manifest_handler.lambda_handler`](./national-document-repository/lambdas/handlers/generate_document_manifest_handler.py)

**Type**: SQS-triggered  
**Description**: Generates document manifests asynchronously

### - Generate Lloyd George Stitch

**Handler**: [`generate_lloyd_george_stitch_handler.lambda_handler`](./national-document-repository/lambdas/handlers/generate_lloyd_george_stitch_handler.py)

**Type**: SQS-triggered  
**Description**: Performs the actual PDF stitching for Lloyd George records

### - Login Redirect

**Handler**: [`login_redirect_handler.lambda_handler`](./national-document-repository/lambdas/handlers/login_redirect_handler.py)

**Type**: HTTP-triggered (separate endpoint)  
**Description**: Handles OAuth2 login redirects

### - Manage NRL Pointer

**Handler**: [`manage_nrl_pointer_handler.lambda_handler`](./national-document-repository/lambdas/handlers/manage_nrl_pointer_handler.py)

**Type**: SQS-triggered  
**Description**: Manages National Record Locator (NRL) pointers

### - MNS Notification

**Handler**: [`mns_notification_handler.lambda_handler`](./national-document-repository/lambdas/handlers/mns_notification_handler.py)

**Type**: SQS-triggered  
**Description**: Processes MNS (Messaging Notification Service) notifications

### - NHS OAuth Token Generator

**Handler**: [`nhs_oauth_token_generator_handler.lambda_handler`](./national-document-repository/lambdas/handlers/nhs_oauth_token_generator_handler.py)

**Type**: Event-driven  
**Description**: Generates OAuth tokens for NHS services

### - PDF Stitching

**Handler**: [`pdf_stitching_handler.lambda_handler`](./national-document-repository/lambdas/handlers/pdf_stitching_handler.py)

**Type**: SQS-triggered  
**Description**: Generic PDF stitching service

### - Statistical Report

**Handler**: [`statistical_report_handler.lambda_handler`](./national-document-repository/lambdas/handlers/statistical_report_handler.py)

**Type**: Scheduled  
**Description**: Generates statistical reports for the system

### - FHIR Document Reference Search

**Handler**: [`fhir_document_reference_search_handler.lambda_handler`](./national-document-repository/lambdas/handlers/fhir_document_reference_search_handler.py)

**Type**: API Gateway (GET on `/DocumentReference`)  
**Authorization**: API Key  
**Description**: FHIR-compliant document reference search (non-production only)

### - Get FHIR Document Reference

**Handler**: [`get_fhir_document_reference_handler.lambda_handler`](./national-document-repository/lambdas/handlers/get_fhir_document_reference_handler.py)

**Type**: API Gateway (via APIM)  
**Description**: Retrieves specific FHIR document references

---

## Common Response Formats

### Success Response

```json
{
  "statusCode": 200,
  "body": {
    // Response data
  },
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true"
  }
}
```

### Error Response

```json
{
  "statusCode": 400|401|403|404|500,
  "body": {
    "message": "Error description",
    "error": "ERROR_CODE"
  }
}
```

## Environment Variables

Common environment variables used across Lambda functions:

- `WORKSPACE` - Deployment environment
- `APPCONFIG_APPLICATION` - AWS AppConfig application ID
- `APPCONFIG_ENVIRONMENT` - AWS AppConfig environment ID
- `APPCONFIG_CONFIGURATION` - AWS AppConfig configuration profile ID
- `PDS_FHIR_IS_STUBBED` - Whether PDS is stubbed (sandbox environments)
- `SPLUNK_SQS_QUEUE_URL` - SQS queue for audit logging
- Various DynamoDB table names and S3 bucket names

## Security Considerations

1. All patient-facing endpoints require authentication
2. API Gateway uses custom authorizer for token validation
3. CORS is configured per environment
4. Virus scanning is performed on all uploaded documents
5. Audit logging is implemented for compliance
6. Sensitive data is encrypted at rest and in transit

## Rate Limiting

API Gateway implements rate limiting to prevent abuse. Specific limits vary by endpoint and environment.

## Monitoring and Observability

- CloudWatch Logs for all Lambda functions
- X-Ray tracing enabled for performance monitoring
- Custom CloudWatch alarms for critical functions
- Splunk integration for centralized logging
