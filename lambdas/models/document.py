import pathlib


class Document:
    def __init__(self, nhs_number, file_name, virus_scanner_result, file_location):
        self.nhs_number = nhs_number
        self.file_name = file_name
        self.file_name_path = pathlib.Path(self.file_name)
        self.virus_scanner_result = virus_scanner_result
        self.file_location = file_location

    def get_base_name(self):
        return self.file_name_path.stem

    def get_file_extension(self):
        return self.file_name_path.stem

    def get_file_key(self):
        return self.file_location.replace("s3://", "").split("/", 1)[1]
