# National Document Repository: Lambdas

This part of the repository contains all our Lambda functions, currently these include...

- create_document_reference_handler
- search_patient_details_handler
- document_reference_search_handler

## Prerequisite

This project will be using Python 3.11. Install this on your machine from https://www.python.org/downloads/

Alternatively, you can set up `pyenv` to handle multiple Python versions:

### Mac/Linux

https://github.com/pyenv/pyenv

### Windows

https://github.com/pyenv-win/pyenv-win

## Virtual Environment

To setup the Python environment for backend development, run: `make env`

This will create a virtual environment with all production and test requirements. The virtual environment can be found
at `.lambdas/venv`.

To activate the environment in Mac/Linux or UNIX based Windows terminal, run:
`source ./lambdas/venv/bin/activate`

To activate in Windows terminals, run:
`./lambdas/venv/Scripts/activate`

## Local Deployment to AWS instructions

To create a deployable zip package for the AWS lambdas, run: `make package`

This will install production dependancies and copy our files into to `lambdas/package`. This folder will then be zipped
as `lambdas/package/lambdas.zip` and ready to deploy to AWS either manually or through github actions.

- Readme modification to trigger build
- Second Trigger

## Repository best practices

(TBA)

## About Lambda functions

### document_reference_search_handler

This lambda search multiple Dynamo DB tables for a patient's records, and return the location of records in S3 buckets.

Require input value:

- queryStringParameters: `patientId` (string, 10 digits, nhs number)

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

### create_document_reference_handler

This lambda creates a document reference in Dynamo DB table,
and creates a presign url to upload the document to S3 bucket.

If successful, the lambda will return status 200 with presign URL of s3 bucket.

### search_patient_details_handler

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

### document_reference_search_handler

This lambda is used to search DynamoDB for the documents uploaded against a patient's NHS number.

It only returns what is required to display on the frontend page, notably any file names, times the files were
originally uploaded and the result of the virus scan.

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

```
patientId=9449305552
```

Hitting URL directly:

```
https://{url}/SearchDocumentReferences?patientId=9449305552
```

#### Possible outputs

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
  "body": "[{\"FileName\": \"nhs1-3669038588 (1).png\", \"Created\": \"2023-09-05T08:34:15.662364Z\"}, {\"FileName\": \"nhs1-test-lloyd-george (1).png\", \"Created\": \"2023-09-05T08:34:15.662364Z\", \"VirusScannerResult\": \"Clean\"}]"
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

### document_manifest_by_nhs_number_handler

The manifest lambda expects two query string parameters called patientId and docType.

**patientId** is to be supplied as a String, and should conform to standard NHS Number format

**docType** is a String and expects a single or comma-seperated list of types of document you're searching for.
It can be set to the following values:

For just Lloyd George docs "LG"

For just ARF docs "ARF"

For all docs "LG,ARF"

If the parameter is not supplied, the values contain something unspecified, or it is an empty String, a 400 error will be returned

hi