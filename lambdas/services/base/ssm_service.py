import boto3


class SSMService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialised = False
        return cls._instance

    def __init__(self):
        if not self.initialised:
            self.client = boto3.client("ssm", region_name="eu-west-2")
            self.initialised = True

    def get_ssm_parameter(self, parameter_key: str, with_decryption=False):
        ssm_response = self.client.get_parameter(
            Name=parameter_key, WithDecryption=with_decryption
        )
        return ssm_response["Parameter"]["Value"]

    def get_ssm_parameters(self, parameters_keys: list[str], with_decryption=False):
        ssm_response = self.client.get_parameters(
            Names=parameters_keys, WithDecryption=with_decryption
        )
        return {
            parameter["Name"]: parameter["Value"]
            for parameter in ssm_response["Parameters"]
        }

    def update_ssm_parameter(
        self, parameter_key: str, parameter_value: str, parameter_type: str
    ):
        self.client.put_parameter(
            Name=parameter_key,
            Value=parameter_value,
            Type=parameter_type,
            Overwrite=True,
        )
