from pydantic import ConfigDict
import inflection


def to_camel(string: str) -> str:
    return inflection.camelize(string, uppercase_first_letter=False)


conf = ConfigDict(alias_generator=to_camel)
