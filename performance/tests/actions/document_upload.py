from locust import HttpUser


def upload_document(client: HttpUser, pdfInstruction):
    raw_values = {
        "key": pdfInstruction["key"],
        "x-amz-algorithm": pdfInstruction["x-amz-algorithm"],
        "x-amz-credential": pdfInstruction["x-amz-credential"],
        "x-amz-date": pdfInstruction["x-amz-date"],
        "x-amz-security-token": pdfInstruction["x-amz-security-token"],
        "policy": pdfInstruction["policy"],
        "x-amz-signature": pdfInstruction["x-amz-signature"],
    }

    # Read part of a PDF file
    pdf_file_path = (
        f"./data/{pdfInstruction['nhsNumber']}/"
        f"{pdfInstruction['currentPage']}of"
        f"{pdfInstruction['lastPage']}_Lloyd_George_Record_"
        f"[Brad Edmond Avery]_[9730787212]_[13-09-2006]"
    )

    pdf_part = []

    with open(pdf_file_path, "rb") as f:
        pdf_part.append(("", ("file", f, "application/octet-stream")))

        # Upload the file
        response = client.client.post(
            pdfInstruction["url"], data=raw_values, files=pdf_part
        )

    return response

