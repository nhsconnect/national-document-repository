#!/bin/bash

# Replace "your-aws-profile" with the appropriate profile name within .aws/config
profile="your-aws-profile"

# Replace 'your-bucket-name' with the S3 bucket name
bucket_name="your-bucket-name"

# List of directories within the bucket - replace "directory" accordingly
directories=(
"directory"
"directory"
)

##############################

# Initialize total file count
total_file_count=0

# Function to count files in a directory
count_files_in_directory() {
    local directory="$1"
    local file_count=$(aws s3 ls "s3://$bucket_name/$directory" --recursive --profile $profile | wc -l)
    echo "Number of files in '$directory': $file_count"
    total_file_count=$((total_file_count + file_count))
}

# Iterate through the list of directories
for dir in "${directories[@]}"; do
    count_files_in_directory "$dir"
done

echo "Total number of files in all directories: $total_file_count"
