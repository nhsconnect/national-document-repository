from enums.dynamo_filter import AttributeOperator, ConditionOperator
from enums.metadata_field_names import DocumentReferenceMetadataFields
from utils.dynamo_query_filter_builder import DynamoQueryFilterBuilder

NotDeleted = (
    DynamoQueryFilterBuilder()
    .add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.EQUAL,
        filter_value="",
    )
    .build()
)

UploadCompleted = (
    DynamoQueryFilterBuilder()
    .add_condition(
        attribute=str(DocumentReferenceMetadataFields.DELETED.value),
        attr_operator=AttributeOperator.EQUAL,
        filter_value="",
    )
    .add_condition(
        attribute=str(DocumentReferenceMetadataFields.UPLOADED.value),
        attr_operator=AttributeOperator.EQUAL,
        filter_value=True,
    )
    .set_combination_operator(ConditionOperator.AND)
    .build()
)
