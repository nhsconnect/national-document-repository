import json

from models.sqs.pdf_stitching_sqs_message import PdfStitchingSqsMessage


def test_handler_parses_sqs_message():
    body = (
        '{"nhs_number": "9730787506", '
        '"snomed_code_doc_type": {"code": "16521000000101", "display_name": "Lloyd George record folder"}}'
    )
    message_body = json.loads(body)
    stitching_message = PdfStitchingSqsMessage.model_validate(message_body)

    print(stitching_message)
