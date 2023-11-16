from pulumi import Config

from utils.helpers import merge_opts
from utils.synthesizer import synthesize

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
from gcp import cloudsql as gcp_sql

from utils.azure import setup_azure
from azure import functionapp as azure_functionapp
from azure import storageblob as azure_storageblob


class Monad:
    def __init__(self):
        config = Config()
        self.cloud_provider = config.require("cloud_provider")
        if self.cloud_provider == "gcp":
            self.google_provider, self.gcp_lambda_bucket, self.gcp_lambda_archive = setup_gcp()
        elif self.cloud_provider == "aws":
            pass
        elif self.cloud_provider == "azure":
            self.azure_resource_group, self.azure_account, self.storage_container, self.azure_service_plan = setup_azure()

    def create_apigw(self, name, routes, opts=None):
        if self.cloud_provider == "aws":
            return aws_apigw.create_apigw(name, routes, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_apigw.create_apigw(name, routes, opts=merge_opts(self.google_provider, opts))
        elif self.cloud_provider == "azure":
            pass

    def create_lambda(self, name, handler, role=None, environment={}, http_trigger=True, mq_topic=None, min_instance=1,
                      max_instance=3, ram=256, timeout_seconds=60, opts=None):
        synthesize(handler, http_trigger, environment)
        if self.cloud_provider == "aws":
            return aws_lambda.create_lambda(name, handler, role, environment,
                                            http_trigger=http_trigger, sqs=mq_topic,
                                            ram=ram, timeout_seconds=timeout_seconds,
                                            opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_lambda.create_lambdav2(name, handler, role, environment,
                                              http_trigger=http_trigger, topic=mq_topic,
                                              source_bucket=self.gcp_lambda_bucket,
                                              bucket_archive=self.gcp_lambda_archive,
                                              min_instance=min_instance, max_instance=max_instance,
                                              ram=ram, timeout_seconds=timeout_seconds, opts=opts)
        elif self.cloud_provider == "azure":
            #blob = azure_storageblob.create_storage_blob(name, handler.split(".")[0], azure_config=(
            #self.azure_resource_group, self.azure_account, self.storage_container, self.azure_service_plan), opts=opts)
            func = azure_functionapp.create_function_app(name, handler, environment, http_trigger=http_trigger, sqs=mq_topic,
                                                         ram=ram, azure_config=(
                self.azure_resource_group, self.azure_account, self.storage_container, self.azure_service_plan),
                                                         opts=opts)
            return func

    def create_sns_topic(self, name, opts=None):
        if self.cloud_provider == "aws":
            return aws_snssqs.create_sns_topic(name, opts=opts)
        elif self.cloud_provider == "gcp":
            pass
        elif self.cloud_provider == "azure":
            pass

    def create_message_queue(self, topic_name, message_retention_seconds="60s", environment={}, opts=None):
        if self.cloud_provider == "aws":
            return aws_snssqs.create_sqs(topic_name, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_pubsub.create_pubsub(topic_name, message_retention_seconds=message_retention_seconds,
                                            opts=opts), environment
        elif self.cloud_provider == "azure":
            pass

    def get_instance_class_sql(self, name):
        if self.cloud_provider == "aws":
            if name == "small":
                return "db.t3.micro"
        elif self.cloud_provider == "gcp":
            if name == "small":
                return "db-f1-micro"
        elif self.cloud_provider == "azure":
            pass

    def create_sql_database(self, name, engine, engine_version, storage, username, password, instance_class, opts=None):
        instance_class = self.get_instance_class_sql(instance_class)
        if self.cloud_provider == "aws":
            return aws_sql.create_sql_database(name, engine, engine_version, storage, username,
                                               password, instance_class, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_sql.create_sql_database(name, engine, engine_version, username,
                                               password, instance_class, opts=opts)
        elif self.cloud_provider == "azure":
            pass

    def iam_role_json(self, name):
        if self.cloud_provider == "aws":
            if name == "lambda-role":
                return "policy/aws/lambda-apigw.json"
            elif name == "mq-role":
                return "policy/aws/lambda-mq.json"
        elif self.cloud_provider == "gcp":
            if name == "lambda-role":
                return "roles/cloudfunctions.invoker"
            elif name == "mq-role":
                return "roles/cloudfunctions.invoker"
        elif self.cloud_provider == "azure":
            pass

    def create_iam_role(self, name, rolefile, opts=None):
        rolefile = self.iam_role_json(rolefile)
        if self.cloud_provider == "aws":
            return aws_iam.create_iam_role(name, rolefile, opts=opts)
        elif self.cloud_provider == "gcp":
            return gcp_iam.create_iam_role(name, rolefile)
        elif self.cloud_provider == "azure":
            pass

    def create_role_policy_attachment(self, rolename, rolefile, name, policyname, policyfile, opts=None):
        rolefile, policyfile = self.iam_role_json(rolefile), self.iam_role_json(policyfile)
        if self.cloud_provider == "aws":
            return aws_iam.create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=opts)
        elif self.cloud_provider == "gcp":
            pass
        elif self.cloud_provider == "azure":
            pass

    def create_iam(self, rolename, rolefile, name=None, policyname=None, policyfile=None, opts=None):
        if self.cloud_provider == "aws":
            if name is None:
                return self.create_iam_role(rolename, rolefile, opts=opts)
            else:
                return self.create_role_policy_attachment(rolename, rolefile, name, policyname, policyfile, opts=opts)
        elif self.cloud_provider == "gcp":
            return self.create_iam_role(name, rolefile, opts=opts)
        elif self.cloud_provider == "azure":
            pass
