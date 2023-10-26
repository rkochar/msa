from pulumi import Config

from aws import apigw as aws_apigw
from aws import lambdafunction as aws_lambda
from aws import iam as aws_iam
from aws import snssqs as aws_snssqs
from aws import sql as aws_sql

from gcp import apigw as gcp_apigw
from gcp import iam as gcp_iam
from gcp import lambdafunction as gcp_lambda
from gcp import pubsub as gcp_pubsub
from gcp import sql as gcp_sql

# import azure

config = Config()
cloud_provider = config.require("cloud_provider")
print(f"Cloud provider is {cloud_provider}")


def create_apigw(name, routes, opts=None):
    if cloud_provider == "aws":
        return aws_apigw.create_apigw(name, routes, opts=opts)
    elif cloud_provider == "gcp":
        return gcp_apigw.create_apigw(name, routes, opts=opts)
    elif cloud_provider == "azure":
        pass


def create_iam_role(name, file, opts=None):
    if cloud_provider == "aws":
        return aws_iam.create_iam_role(name, file, opts=opts)
    elif cloud_provider == "gcp":
        return gcp_iam.create_iam_role(name)
    elif cloud_provider == "azure":
        pass


def create_lambda(name, handler, role, environment=None, project="", opts=None):
    if cloud_provider == "aws":
        return aws_lambda.create_lambda(name, handler, role, environment, project=project, opts=opts)
    elif cloud_provider == "gcp":
        return gcp_lambda.create_lambda(name, handler, role, environment, project=project, opts=opts)
    elif cloud_provider == "azure":
        pass


def create_sns_topic(name, opts=None):
    if cloud_provider == "aws":
        return aws_snssqs.create_sns_topic(name, opts=opts)
    elif cloud_provider == "gcp":
        return gcp_pubsub.create_pubsub(name, opts=opts)
    elif cloud_provider == "azure":
        pass


def create_sqs(name, opts=None):
    if cloud_provider == "aws":
        return aws_snssqs.create_sqs(name, opts=opts)
    elif cloud_provider == "gcp":
        pass
    elif cloud_provider == "azure":
        pass


def create_iam_policy(name, file, opts=None):
    if cloud_provider == "aws":
        return aws_iam.create_iam_policy(name, file, opts=opts)
    elif cloud_provider == "gcp":
        pass
    elif cloud_provider == "azure":
        pass


def create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=None):
    if cloud_provider == "aws":
        return aws_iam.create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=opts)
    elif cloud_provider == "gcp":
        pass
    elif cloud_provider == "azure":
        pass


def create_sql_database(name, engine, engine_version, storage, instance_class, username, password, opts=None):
    if cloud_provider == "aws":
        return aws_sql.create_sql_database(name, engine, engine_version, storage, instance_class, username, password, opts=opts)
    elif cloud_provider == "gcp":
        return gcp_sql.create_sql_database(name, engine, engine_version, storage, instance_class, username, password, opts=opts)
    elif cloud_provider == "azure":
        pass