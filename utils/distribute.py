from pulumi import Config

from aws import apigw as aws_apigw
from aws import lambdafunction as aws_lambda
from aws import iam as aws_iam
from aws import snssqs as aws_snssqs
from aws import sql as aws_sql

from utils.gcp import setup_gcp
from gcp import apigw as gcp_apigw
from gcp import iam as gcp_iam
from gcp import cloudfunction as gcp_lambda
from gcp import pubsub as gcp_pubsub
from gcp import sql as gcp_sql


# import azure

class Distribute:
    def __init__(self):
        config = Config()
        self.cloud_provider = config.require("cloud_provider")
        if self.cloud_provider == "gcp":
            self.google_provider, self.gcp_lambda_bucket, self.gcp_lambda_archive = setup_gcp()
        elif self.cloud_provider == "aws":
            pass
        elif self.cloud_provider == "azure":
            pass

    def create_apigw(self, name, routes, opts=None):
        if self.cloud_provider == "aws":
            return aws_apigw.create_apigw(name, routes, opts=opts)
        elif self.cloud_provider == "gcp":
            # TODO: Merge opts for GCP
            return gcp_apigw.create_apigw(name, routes, opts=self.google_provider)
        elif self.cloud_provider == "azure":
            pass

    def create_iam_role(self, name, rolefile, opts=None):
        if self.cloud_provider == "aws":
            return aws_iam.create_iam_role(name, rolefile, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_iam.create_iam_role(name, rolefile)
        elif self.cloud_provider == "azure":
            pass

    def iam_role_json(self, name):
        if self.cloud_provider == "aws":
            if name == "lambda-role":
                return "policy/aws/lambda-apigw.json"
        elif self.cloud_provider == "gcp":
            if name == "lambda-role":
                return "roles/cloudfunctions.invoker"
        elif self.cloud_provider == "azure":
            pass

    def create_lambda(self, name, handler, role, environment={}, opts=None):
        if self.cloud_provider == "aws":
            return aws_lambda.create_lambda(name, handler, role, environment, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_lambda.create_lambda(name, handler.split("."), role, environment,
                                            source_bucket=self.gcp_lambda_bucket,
                                            bucket_archive=self.gcp_lambda_archive, opts=opts)
        elif self.cloud_provider == "azure":
            pass

    def create_sns_topic(self, name, opts=None):
        if self.cloud_provider == "aws":
            return aws_snssqs.create_sns_topic(name, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_pubsub.create_pubsub(name, opts=opts)
        elif self.cloud_provider == "azure":
            pass

    def create_sqs(self, name, opts=None):
        if self.cloud_provider == "aws":
            return aws_snssqs.create_sqs(name, opts=opts)
        elif self.cloud_provider == "gcp":
            pass
        elif self.cloud_provider == "azure":
            pass

    def create_iam_policy(self, name, file, opts=None):
        if self.cloud_provider == "aws":
            return aws_iam.create_iam_policy(name, file, opts=opts)
        elif self.cloud_provider == "gcp":
            pass
        elif self.cloud_provider == "azure":
            pass

    def create_role_policy_attachment(self, name, policyname, policyfile, rolename, rolefile, opts=None):
        if self.cloud_provider == "aws":
            return aws_iam.create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=opts)
        elif self.cloud_provider == "gcp":
            pass
        elif self.cloud_provider == "azure":
            pass

    def create_sql_database(self, name, engine, engine_version, storage, instance_class, username, password, opts=None):
        if self.cloud_provider == "aws":
            return aws_sql.create_sql_database(name, engine, engine_version, storage, instance_class, username,
                                               password, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_sql.create_sql_database(name, engine, engine_version, storage, instance_class, username,
                                               password, opts=opts)
        elif self.cloud_provider == "azure":
            pass
