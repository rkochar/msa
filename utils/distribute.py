from pulumi import Config

from aws import apigw as aws_apigw
from aws import lambdafunction as aws_lambda
from aws import iam as aws_iam

from gcp import apigw as gcp_apigw

# import azure

config = Config()
cloud_provider = config.require("cloud_provider")
print(f"Cloud provider is {cloud_provider}")


def create_apigw(name, routes):
    if cloud_provider == "aws":
        return aws_apigw.create_apigw(name, routes)
    elif cloud_provider == "gcp":
        return gcp_apigw.create_apigw(name, routes)
    elif cloud_provider == "azure":
        pass


def create_iam_role(name, file):
    if cloud_provider == "aws":
        return aws_iam.create_iam_role(name, file)
    elif cloud_provider == "gcp":
        pass
    elif cloud_provider == "azure":
        pass


def create_lambda(name, handler, role):
    if cloud_provider == "aws":
        return aws_lambda.create_lambda(name, handler, role)
    elif cloud_provider == "gcp":
        pass
    elif cloud_provider == "azure":
        pass