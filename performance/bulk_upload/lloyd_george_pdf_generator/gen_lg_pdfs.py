"""
Generate Lloyd George Record PDFs from CSV

Generates test Lloyd George PDF Records for individuals based on data provided
in a CSV file.

The CSV file should contain and adhere to the following headers:
- NHS_NUMBER            10 digit NHS number
- DATE_OF_BIRTH         (DD/MM/YYYY or YYYYMMDD)
- FAMILY_NAME           string
- GIVEN_NAME            string
- OTHER_GIVEN_NAME      string (optional)

The generated records are organized into folders named by NHS_NUMBER within a
specified root directory. Each folder contains three PDF pages:
1. A blank 'front' page
2. A page filled with random text to make up a maximum file size requirement
3. Another blank 'back' page

The script also creates a metadata.csv file in the root directory.

Usage:
- Amend input_file and root_directory accordingly
- Make sure the input CSV file follows the specified format
- Run the script: `python gen_lg_pdfs.py`

Version:
- 1.0 (2023-11-14): PRM Bulk Upload Performance Test
"""

import csv
import os
from fpdf import FPDF
import shutil
import random
import string
from datetime import datetime


# Define input file
input_file = "input_datasets/input_dataset.csv"

# Define the root directory for storing folders and PDFs
root_directory = "output_datasets"

# Delete the root directory if it exists
if os.path.exists(root_directory):
    shutil.rmtree(root_directory)

# Create the root directory
os.mkdir(root_directory)


# Function to generate random text for PDF page 2 (noise)
def generate_noise_text(target_size_mb=1):
    target_size_bytes = int(target_size_mb * 1024 * 1024)
    text = ""
    while len(text.encode("utf-8")) < target_size_bytes:
        text += "".join(random.choice(string.ascii_letters) for _ in range(1024))
    return text[:target_size_bytes]


# Function to create the template PDF files
def get_template_pdf(file_path, text=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=text)

    # Open the file in binary write mode and write the PDF content
    pdf.output(file_path, "F")


# Create or load the blank template PDF for pages 1 and 3
blank_template_path = os.path.join("templates", "blank_template.pdf")
get_template_pdf(blank_template_path)

# Create or load the noise template PDF for page 2
noise_template_path = os.path.join("templates", "noise_template.pdf")
noise_text = generate_noise_text()
get_template_pdf(noise_template_path, noise_text)

# Create metadata.csv file
metadata_file = open(os.path.join(root_directory, "metadata.csv"), "w", newline="")
metadata_writer = csv.writer(metadata_file)
metadata_writer.writerow(
    [
        "FILEPATH",
        "PAGE COUNT",
        "GP-PRACTICE-CODE",
        "NHS-NO",
        "SECTION",
        "SUB-SECTION",
        "SCAN-DATE",
        "SCAN-ID",
        "USER-ID",
        "UPLOAD",
    ]
)

# Read data from the input CSV file
with open(input_file, newline="") as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        # Create a folder for each NHS_NUMBER
        folder_name = os.path.join(root_directory, row["NHS_NUMBER"])
        os.mkdir(folder_name)

        # Combine given names if other given name present in source data
        given_name = row["GIVEN_NAME"]
        if row["OTHER_GIVEN_NAME"]:
            given_name += " " + row["OTHER_GIVEN_NAME"]

        # Format the date of birth
        dob_formatted = row["DATE_OF_BIRTH"]
        try:
            # Attempt to parse the date as "DD/MM/YYYY" format
            dob_datetime = datetime.strptime(dob_formatted, "%d/%m/%Y")
            dob_formatted = dob_datetime.strftime("%d-%m-%Y")
        except ValueError:
            try:
                # If that fails, try parsing as "YYYYMMDD" format
                dob_datetime = datetime.strptime(dob_formatted, "%Y%m%d")
                dob_formatted = dob_datetime.strftime("%d-%m-%Y")
            except ValueError:
                # If neither format matches, keep the original format
                pass

        size = int(row.get("PAGES", 3))
        # Copy template PDFs to the destination folder and rename them
        for page in range(1, size + 1):
            pdf_file_path = os.path.join(
                folder_name,
                f"{page}of{page}_Lloyd_George_Record_[{given_name} {row['FAMILY_NAME']}]_[{row['NHS_NUMBER']}]_[{dob_formatted}].pdf",
            )
            shutil.copyfile(noise_template_path, pdf_file_path)

            # Write metadata to metadata.csv
            metadata_writer.writerow(
                [
                    f"/{os.path.relpath(pdf_file_path, root_directory)}",
                    page,
                    "",
                    row["NHS_NUMBER"],
                    "LG",
                    "",
                    "01/01/2023",
                    "NEC",
                    "NEC",
                    "26/11/2023",
                ]
            )

metadata_file.close()
