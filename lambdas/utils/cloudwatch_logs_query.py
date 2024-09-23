from dataclasses import dataclass


@dataclass
class CloudwatchLogsQueryParams:
    lambda_name: str
    query_string: str


LloydGeorgeRecordsViewed = CloudwatchLogsQueryParams(
    lambda_name="LloydGeorgeStitchLambda",
    query_string="""
        fields @timestamp, Message, Authorisation.selected_organisation.org_ods_code AS ods_code 
        | filter Message = 'User has viewed Lloyd George records' 
        | stats count() AS daily_count_viewed BY ods_code
    """,
)

LloydGeorgeRecordsDownloaded = CloudwatchLogsQueryParams(
    lambda_name="DocumentManifestJobLambda",
    query_string="""
        fields @timestamp, Message, Authorisation.selected_organisation.org_ods_code AS ods_code 
        | filter Message = 'User has downloaded Lloyd George records' 
        | stats count() AS daily_count_downloaded BY ods_code
    """,
)

LloydGeorgeRecordsDeleted = CloudwatchLogsQueryParams(
    lambda_name="DeleteDocRefLambda",
    query_string="""
        fields @timestamp, Message, Authorisation.selected_organisation.org_ods_code AS ods_code 
        | filter Message = "Deleted document of type LG"
        | stats count() AS daily_count_deleted BY ods_code
    """,
)

LloydGeorgeRecordsStored = CloudwatchLogsQueryParams(
    lambda_name="UploadConfirmResultLambda",
    query_string="""
        fields @timestamp, Message, Authorisation.selected_organisation.org_ods_code AS ods_code
        | filter Message = 'Finished processing all documents'
        | stats count() AS daily_count_stored BY ods_code
    """,
)

LloydGeorgeRecordsSearched = CloudwatchLogsQueryParams(
    lambda_name="SearchPatientDetailsLambda",
    query_string="""
        fields @timestamp, Message, Authorisation.selected_organisation.org_ods_code AS ods_code
        | filter Message = 'Searched for patient details' 
        | stats count() AS daily_count_searched BY ods_code
    """,
)


UniqueActiveUserIds = CloudwatchLogsQueryParams(
    lambda_name="AuthoriserLambda",
    query_string="""
        fields @timestamp, Authorisation.selected_organisation.org_ods_code AS ods_code, Authorisation.nhs_user_id AS user_id
        | filter ispresent(ods_code) AND ispresent(user_id)
        | dedup(ods_code, user_id)
    """,
)
