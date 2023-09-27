from utils.exceptions import InvalidResourceIdException


def validate_id(patient_id: str) -> bool:
    pattern = re.compile("^\\d{10}$")

    if not bool(pattern.match(patient_id)):
        raise InvalidResourceIdException("Invalid NHS number")

    return True


def decapitalise_keys(values):
    data = {}
    for key, value in values.items():
        data[key[0].lower() + key[1:]] = value
    return data
