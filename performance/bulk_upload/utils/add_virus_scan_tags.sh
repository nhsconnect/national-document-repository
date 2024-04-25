#!/bin/bash

# Replace "your-aws-profile" with the appropriate profile name within .aws/config
profile="your-aws-profile"

# Replace 'your-bucket-name' with the S3 bucket name
bucket_name="your-bucket-name"

# List of directories within the bucket for which to update tags - replace "directory" accordingly
directories=(
  "directory"
  "directory"
)

# Specify the date for the date-scanned tag
scan_result="Clean"
date_scanned="2023-11-23T15:50:33Z"

# Loop through each directory
for dir in "${directories[@]}"
do
  # List objects in the directory and extract keys with jq
  objects=$(aws s3api list-objects --bucket "$bucket_name" --prefix "$dir" --output json --query 'Contents[].{Key: Key}' --profile $profile)

  # Loop through each object and update the 'scan-result' and 'date-scanned' tags
  echo "$objects" | jq -r '.[].Key' | while IFS= read -r object; do
    aws s3api put-object-tagging --bucket "$bucket_name" --key "$object" --tagging "TagSet=[{Key=scan-result,Value=$scan_result},{Key=date-scanned,Value=$date_scanned}]" --profile $profile
    echo "Updated 'scan-result' and 'date-scanned' tags for $object"
  done
done