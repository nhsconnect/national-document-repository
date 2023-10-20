import pathlib


class Document:
    def __init__(self, nhs_number, file_name, virus_scanner_result, file_location):
        self.nhs_number = nhs_number
        self.file_name = file_name
        self.virus_scanner_result = virus_scanner_result
        self.file_location = file_location

        self.file_name_path = pathlib.Path(self.file_name)
        self.file_bucket, self.file_key = self.file_location.replace("s3://", "").split(
            "/", 1
        )

    def get_base_name(self):
        return self.file_name_path.stem

    def get_file_extension(self):
        return self.file_name_path.suffix

    def create_unique_filename(self, duplicates):
        return f"{self.get_base_name()}({duplicates}){self.get_file_extension()}"

    def __eq__(self, other):
        if isinstance(self, Document):
            return (
                self.nhs_number == other.nhs_number
                and self.file_name == other.file_name
                and self.virus_scanner_result == other.virus_scanner_result
                and self.file_location == other.file_location
            )
        return False
