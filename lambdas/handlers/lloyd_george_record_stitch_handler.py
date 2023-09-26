

def lambda_handler(event, context):

    # Get the patient's list of docs from the NDR LG Dynamo table
    # Download them all in order, their filenames should impose an order
    # File names are stored in Dynamo which is why we need it first
    # Stitch them together in order
    # upload them to S3 - set a TTL on the bucket
    # return pre-signed URL to download and send it to the UI using api response

    pass
