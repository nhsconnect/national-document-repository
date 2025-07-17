# Migration Assessment

## Intro

The following fields represent the state of the NDR post merge NDR-100, the goal of this document is to highlight what will need to change as part of the migration, what needs to change and additional work required before the migration takes place.

## Fields

This document will detail a field by field level of the status of each record in the database what it will need to become and what is still required.

Please refer to the following JSON resource as this represents a full FHIR record for a patient record and reflects the metadata

```json
{
    "id": "d90f9546-daff-47b6-b36b-99cc8b14d75a",
    "resourceType": "DocumentReference",
    "docStatus": "final",
    "status": "current",
    "type": {
        "coding": [
            {
                "system": "http://snomed.info/sct",
                "code": "16521000000101",
                "display": "Lloyd George record folder"
            }
        ]
    },
    "subject": {
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": "9730168326"
        }
    },
    "date": "2025-07-07T11:03:41.638660Z",
    "author": [
        {
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "H81109"
            }
        }
    ],
    "custodian": {
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "H81109"
        }
    },
    "content": [
        {
            "attachment": {
                "contentType": "application/pdf",
                "language": "en-GB",
                "size": 329035,
                "title": "1of1_Lloyd_George_Record_[historical sarah]_[9730168326]_[27-12-1962].pdf",
                "creation": "2023-01-01",
                "data": "{redacted}"
            }
        }
}
```

### ID

Mapping from ID (Dynamo) to ID FHIR\*\*

**This field does not need to be migrated**

### resourceType

This is always `DocumentReference` and does not have a corresponding Dynamo Entry. (All Files are of type 'DocumentReference')

### docStatus

Mapping from docStatus to DocStatus

- Reflects the status of the Document
- This differs from 'status' that reflects the status of the Document reference.

There are 3 key statuses

- Deprecated (The document is deleted)
- Final (The document is currently in use and is the stated record)
- Preliminary (Used during processing to incurr the record is not ready for consumption)

If a file is marked for 'deletion' Which I think is the `Deleted` field and includes a TTL then we will need to highlight the docStatus as 'Deprecated' this is only for files that are pending deletion which were deleted prior to the deployment of NDR-100

The deleted status is still in discussion
https://nhsd-jira.digital.nhs.uk/browse/NDR-134

Final, all current active records should be migrated to this state.

Preliminary, all `uploading` files should be migrated to this state.

### status

Maps to Status in the DynamoDB

Represents the status of the reference to the record. There are still discussions pending regarding the usage of the status of this field so this may change.

https://nhsd-jira.digital.nhs.uk/browse/NDR-134

There are two possible status
`current`
`superseded`

Wait for outcomes of NDR-134 for migration instructions

### type

#### type.coding[0].code

This maps to the DynamoDB entry DocumentSnomedCode
While not intuitive because the record type is inferred via the Database name, we need to indicate this as the PDM use case may use different types.

For _all_ records in the LloydGeorgeDynamoDB where the snomedcode is not present this can be set as: 16521000000101

All other type fields are supplementary FHIR data e.g. Textual Descriptions

### subject.identifier.value[0]

This maps to the NHS number no migration needs to be performed here and this field remains the same both pre and post NDR-100

System is also here but is just a description of what the field represents

### date

The date is mapped to 'Created' in DynamoDB No migration required here, represents the date the file was uploaded to the NDR.

### author

Maps to 'Author' DynamoDB field.

There is a ongoing bug with NDR-100 whgre carrying forward BulkUpload will need to provide the Author at point of ingestion. https://nhsd-jira.digital.nhs.uk/browse/NDR-169

The Author can be interpreted from the BulkUploadTable as this represents historically who originally uploaded the record.
This will need to be performed on old style AND new style records (Records created via other means e.g. Bulk Upload post NDR-100 or modified e.g. via deletion or modified via MNS)

### custodian

The custodian represents the current owner of the LloydGeorgeRecord, this maps to the CurrentGpOds HOWEVER there is an important distinction between Custodian and CurrentGpOds

The CurrentGpOds is also used to store patient state in scenarios where the Patient is DECE, SUSP or REST. This doesn't represent the custodian in FHIR since this is as far as FHIR goes will be interpreted as the PCSE ODS code e.g. 'X12345'.

The following migration should take place.

- The CurrentGpODSCode should be used for the Custodian field and be preserved.
- If the CurrentGpODSCode is either one of DECE, SUSP or REST then this needs to be interpreted as the current active PCSE role with access to the NDR. The CurrentGPOds needs to be preserved in this instance.

### content>attachment>contentType

This represents the contentType of the record, for LLoydGeorge record this should always be set to 'application/pdf' and will require adding but doesn't come from anywhere pre-existing

### content>attachment>size

Maps to FileSize

This is the size of the record, which is not currently held in the DynamoDB, since we need to migrate this going forward the Migration script needs to read from S3 to interpret the size of the resource at the given FileLocation for that record.

### content>attachment>title

This is reading the 'FileName' field. No migration required here.

### content>attachment>creation

Maps to DocumentScanCreation

This is the scan date of the record which maps to DocumentScanCreation. I don't know where we can interpret this for historic records? Might be one to check with inferred data

### content>attachment>data

The raw dynamo data
