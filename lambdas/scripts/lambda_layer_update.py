import re
import sys

import boto3


class LambdaLayerUpdate:
    def __init__(self):
        self.client = boto3.client("lambda")

        self.environment = sys.argv[1]
        self.function_name_aws = f"{self.environment}_{sys.argv[2]}"
        layers = sys.argv[3].strip().split(",")

        self.updated_lambda_arns = {}
        self.updated_layer_names = []

        print(f"Function Name: {self.function_name_aws}")
        print("Layers to add:")
        for layer in layers:
            updated_layer_name = f"{self.environment}_{layer}"
            self.updated_layer_names.append(updated_layer_name)
            print(f"- {updated_layer_name}")
        print("")

    def start(self):
        self.extract_current_layer_arns()
        self.extract_new_layer_arns()
        self.update_lambda()

    def extract_current_layer_arns(self):
        response = self.client.get_function(FunctionName=self.function_name_aws)
        layer_arns_responses = response["Configuration"]["Layers"]

        for layer_arn_response in layer_arns_responses:
            layer_arn = layer_arn_response["Arn"]
            match = re.search(r"layer:([^:]+):", layer_arn)
            if match:
                layer_name = match.group(1)
                self.updated_lambda_arns.update({layer_name: layer_arn})

    def extract_new_layer_arns(self):
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
    LambdaLayerUpdate.start(LambdaLayerUpdate())
    print("\nUpdate Process Complete.")
