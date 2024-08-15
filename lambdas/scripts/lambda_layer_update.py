import re
import sys

import boto3


class LambdaLayerUpdate:
    def __init__(self):
        self.client = boto3.client("lambda")

        self.sandbox = sys.argv[1]
        self.function_name_aws = f"{self.sandbox}_{sys.argv[2]}"
        layers = sys.argv[3].strip().split(",")

        self.updated_lambda_arns = {}
        self.updated_layer_names = []

        print(f"Function Name: {self.function_name_aws}")
        print("Layers to add:")
        for layer in layers:
            updated_layer_name = f"{self.sandbox}_{layer}"
            self.updated_layer_names.append(updated_layer_name)
            print(f"- {updated_layer_name}")
        print("")

    def start(self):
        self.extract_default_layer_arns()
        self.extract_updated_layer_arns()
        self.update_lambda()

    def extract_default_layer_arns(self):
        response = self.client.get_function(FunctionName=self.function_name_aws)
        if "Layers" not in response["Configuration"]:
            print("Default layers property does not exist in the lambda configuration.")
            return
        else:
            layer_responses = response["Configuration"]["Layers"]
            for layer_response in layer_responses:
                layer_arn = layer_response["Arn"]
                layer_name_match = re.search(r"layer:([^:]+):", layer_arn)
                if layer_name_match:
                    layer_name = layer_name_match.group(1)

                    if layer_name in [
                        "AWS-AppConfig-Extension",
                        "LambdaInsightsExtension",
                    ]:
                        self.updated_lambda_arns.update({layer_name: layer_arn})

    def extract_updated_layer_arns(self):
        for updated_layer_name in self.updated_layer_names:
            print(f"Extracting latest version ARN for {updated_layer_name}...")
            response = self.client.list_layer_versions(LayerName=updated_layer_name)
            latest_layer_version = response["LayerVersions"][0]
            layer_arn = latest_layer_version["LayerVersionArn"]

            self.updated_lambda_arns[updated_layer_name] = layer_arn

    def update_lambda(self):
        print(f"Updating {self.function_name_aws} with new layer ARNs...")
        self.client.update_function_configuration(
            FunctionName=self.function_name_aws,
            Layers=list(self.updated_lambda_arns.values()),
        )


if __name__ == "__main__":
    layer_update = LambdaLayerUpdate()
    layer_update.start()
    print("\nUpdate Process Complete.")
