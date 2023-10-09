class LGFileTypeException(ValueError):
    """One or more of the files do not match the required file type."""
    pass

def validate_lg_file_type(file_type):
    if file_type != 'application/pdf':
        raise LGFileTypeException
