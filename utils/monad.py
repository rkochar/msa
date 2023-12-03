from pulumi import Config

from utils.aws import setup_aws
from utils.azure import setup_azure
from utils.gcp import setup_gcp
from utils.helpers import merge_opts, bash_command, flatten
from utils.synthesizer import synthesize

from aws import apigw as aws_apigw
from aws import lambdafunction as aws_lambda
from aws import iam as aws_iam
from aws import sqs as aws_sqs
from aws import sql as aws_sql

from gcp import apigw as gcp_apigw
from gcp import iam as gcp_iam
from gcp import cloudfunction as gcp_lambda
from gcp import pubsub as gcp_pubsub
from gcp import cloudsql as gcp_sql

from azure import functionapp as azure_functionapp
from azure import storageblob as azure_storageblob
from azure import apimanagement as azure_apigw


class Monad:
    def __init__(self):
        """
        Setup cloud environments.
        AWS requires VPC for RDS and Endpoint for SQS if Lambda is in VPC. Returns s3 code bucket, vpc, security_group, subnet, subnet_group, vpc_endpoint
        GCP requires a Provider. In addition, code of Lambda is added to a Storage bucket. # TODO: Make code optional.
        Azure requires a Resource Group, Storage Account, Storage Container and Service Plan.
        """
        config = Config()
        self.cloud_provider = config.require("cloud_provider")

        match self.cloud_provider:
            case "aws":
                self.aws_config = setup_aws()
            case "gcp":
                self.google_provider, self.gcp_lambda_bucket, self.gcp_lambda_archive = setup_gcp()  # TODO: Move into gcp_config
            case "azure":
                self.azure_config = setup_azure()

    def create_apigw(self, name, routes, opts=None):
        """
        Create APIGW.
        AWS: API Gateway, GCP: APIs, Azure: API Management

        :param name: of APIGW.
        :param routes: see README.md for description of Route. This is a tuple that matches Lambda with path that will trigger it.
        :param opts: of Pulumi
        :return: APIGW object
        """
        match self.cloud_provider:
            case "aws":
                return aws_apigw.create_apigw(name, routes, opts=opts)
            case "gcp":
                return gcp_apigw.create_apigw(name, routes, opts=merge_opts(self.google_provider, opts))
            case "azure":
                return azure_apigw.create_apigw(name, routes, azure_config=self.azure_config, opts=opts)

    def create_lambda(self, code_path, name, handler, role=None, environment={}, template="http", mq_topic=None, sqldb=None, min_instance=1,
                      max_instance=3, ram=256, timeout_seconds=60, imports=False, opts=None):
        """
        Create Lambda and synthesize it's code.
        AWS: Lambda, GCP: Cloud Function, Azure: Function App

        :param imports:
        :param code_path:
        :param name: of Lambda
        :param handler: method that will be called when a Lambda is triggered.
        :param role: IAM role of Lambda
        :param environment: environment variables passed to Lambda
        :param template: type of Lambda: eg. http, mq, sql
        :param mq_topic: if template is not http, SQS object that will trigger Lambda
        :param min_instance: min number of Lambda instances (GCP only)
        :param max_instance: max number of Lambda instances (GCP only)
        :param ram: available to Lambda
        :param timeout_seconds: max timeout of Lambda
        :param opts: of Pulumi
        :return: Lambda object
        """

        synthesize(code_path, handler, template=template, imports=imports)
        http_trigger = True if template.startswith("http") or template == "sql" else False

        match self.cloud_provider:
            case "aws":
                return aws_lambda.create_lambda(code_path, name, handler, role, environment,
                                                template, http_trigger=http_trigger, sqs=mq_topic, sqldb=sqldb,
                                                ram=ram, timeout_seconds=timeout_seconds,
                                                aws_config=self.aws_config, imports=imports, opts=opts)
            case "gcp":
                return gcp_lambda.create_lambdav2(name, handler, role, environment,
                                                  http_trigger=http_trigger, topic=mq_topic,
                                                  source_bucket=self.gcp_lambda_bucket,  # TODO: Change
                                                  bucket_archive=self.gcp_lambda_archive,
                                                  min_instance=min_instance, max_instance=max_instance,
                                                  ram=ram, timeout_seconds=timeout_seconds,
                                                  imports=imports, opts=opts)
            case "azure":
                # blob = azure_storageblob.create_storage_blob(name, handler.split(".")[0], azure_config=self.azure_config, opts=opts)
                func = azure_functionapp.create_function_app(name, handler, environment, http_trigger=http_trigger,
                                                             sqs=mq_topic, ram=ram, azure_config=self.azure_config,
                                                             opts=opts)
                return func

    def create_message_queue(self, topic_name, message_retention_seconds="60s", environment={}, fifo=True, opts=None):
        """
        Create Message Queue.
        AWS: SQS, GCP: Pub/Sub, Azure: tbd.

        :param topic_name: name of Message Queue
        :param message_retention_seconds: timeout of message
        :param environment: of Lambda that will be triggered by MQ (needed for AWS).
        :param fifo: for AWS to force max 1 instance of Lambda (https://stackoverflow.com/a/71208857/12555857)
        :param opts: of Pulumi
        :return: Message Queue object.
        """
        match self.cloud_provider:
            case "aws":
                return aws_sqs.create_sqs(topic_name, fifo=fifo, opts=opts)
            case "gcp":
                return gcp_pubsub.create_pubsub(topic_name, message_retention_seconds=message_retention_seconds,
                                                environment=environment,
                                                opts=opts)
            case "azure":
                pass

    def get_instance_class_sql(self, size):
        """
        Get EC2 instance class for SQL database according to Cloud Provider.

        :param size: "small"
        :return: Correct name according to Cloud Provider.
        """
        match self.cloud_provider:
            case "aws":
                if size == "small":
                    return "db.t3.micro"
            case "gcp":
                if size == "small":
                    return "db-f1-micro"
            case "azure":
                pass

    def create_sql_database(self, name, engine, engine_version, storage, username, password, instance_class, environment={}, opts=None):
        """
        Create SQL database.
        AWS: RDS, GCP: CloudSQL, Azure: tbd

        :param name: of SQL database
        :param engine: "mysql" or "postgres"
        :param engine_version: version of engine
        :param storage: in GB
        :param username: for database
        :param password: for database
        :param instance_class: EC2 instance that will run the database
        :param environment: to be passed to Lambda. It contains information to connect to database
        :param opts: of Pulumi
        :return: SQL database object
        """
        instance_class = self.get_instance_class_sql(instance_class)
        environment["SQLDB_USERNAME"], environment["SQLDB_PASSWORD"] = username, password

        match self.cloud_provider:
            case "aws":
                return aws_sql.create_sql_database(name, engine, engine_version, storage, username,
                                                   password, instance_class, environment, aws_config=self.aws_config, opts=opts)
            case "gcp":
                return gcp_sql.create_sql_database(name, engine, engine_version, username,
                                                   password, instance_class, environment, opts=opts)
            case "azure":
                pass

    def create_sql_command(self, name, handler, template, environment={}, debug=False, opts=None):
        synthesize(handler, template=template)
        python_script_name = handler.replace(".", "_")
        command = bash_command(name, f"python3 {python_script_name}", f"./code/output/{self.cloud_provider}", debug,
                               opts=opts)
        return command

    def iam_role_json(self, name):  # TODO: Use policyname as filemame
        """
        Get IAM role json file path from name of file according to Cloud Provider.

        :param name: of IAM role
        :return: IAM role JSON file path
        """
        match self.cloud_provider:
            case "aws":
                return f"./policy/aws/{name}.json"
            case "gcp":
                return "roles/cloudfunctions.invoker"
            case "azure":
                pass

    def create_iam_role(self, name, roletype, opts=None):
        """
        Create IAM role.

        :param name: of role
        :param roletype: type of IAM role
        :param opts: of Pulumi
        :return: AWS creates IAM role object. GCP returns a string. TODO: fix it. and cleanup. 
        """
        rolefile = self.iam_role_json(roletype)

        match self.cloud_provider:
            case "aws":
                return aws_iam.create_iam_role(name, rolefile, opts=opts)
            case "gcp":
                return rolefile  # gcp_iam.create_iam_role(name, rolefile)
            case "azure":
                pass

    def create_role_policy_attachment(self, rolename, roletype, name, policyname, policytype, opts=None):
        """
        Create IAM Role Policy Attachment (only AWS).

        :param rolename: name of IAM role
        :param roletype: type of IAM role
        :param name: of Role Policy Attachment
        :param policyname: name of policy
        :param policytype: type of policy
        :param opts: of Pulumi
        :return: Role Policy Attachment object
        """
        rolefile, policyfile = self.iam_role_json(roletype), self.iam_role_json(policytype)

        match self.cloud_provider:
            case "aws":
                return aws_iam.create_role_policy_attachment(name, policyname, policyfile, rolename, rolefile, opts=opts)
            case "gcp":
                pass
            case "azure":
                pass

    def create_iam(self, rolename, rolefile, name=None, policyname=None, policyfile=None, opts=None):
        """
        Create IAM roles, policies and attachments.

        :param rolename: name of IAM role
        :param rolefile: type of IAM role
        :param name: of Role Policy Attachment. If None, not created
        :param policyname: name of policy. If None, not created
        :param policyfile: type of policy. If None, not created
        :param opts: of Pulumi
        :return: AWS returns an IAM object. GCP returns a string.
        """
        match self.cloud_provider:
            case "aws":
                if name is None:
                    return self.create_iam_role(rolename, rolefile, opts=opts)
                else:
                    return self.create_role_policy_attachment(rolename, rolefile, name, policyname, policyfile, opts=opts)
            case "gcp":
                return self.create_iam_role(name, rolefile, opts=opts)
            case "azure":
                pass
