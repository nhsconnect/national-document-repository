import re


class LGFileTypeException(ValueError):
    """One or more of the files do not match the required file type"""
    pass

class LGFileNameException(ValueError):
    """One or more of the files do not match naming convention"""
    pass

def validate_lg_file_type(file_type):
    if file_type != 'application/pdf':
        raise LGFileTypeException

def validate_file_name(name):
    lg_regex = '[0-9]+of[0-9]+_Lloyd_George_Record_\\[[A-Za-z]+\\s[A-Za-z]+]_\\[[0-9]{10}]_\\[\\d\\d-\\d\\d-\\d\\d\\d\\d].pdf'
    if not re.fullmatch(lg_regex, name):
        raise LGFileNameException

