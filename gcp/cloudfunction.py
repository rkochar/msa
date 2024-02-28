from pulumi_gcp.cloudfunctionsv2 import Function, FunctionIamMember, FunctionBuildConfigArgs, \
    FunctionBuildConfigSourceArgs, FunctionBuildConfigSourceStorageSourceArgs, FunctionServiceConfigArgs, \
    FunctionEventTriggerArgs
from pulumi import Config, Output, ResourceOptions
from gcp.cloudstorage import create_bucket_object
from pulumi_gcp.storage import Notification, get_project_service_account
from pulumi_gcp.pubsub import TopicIAMBinding
from gcp.pubsub import create_pubsub
from utils.helpers import merge_opts

config = Config("gcp")
region = config.get("region")
project = config.get("project")


def create_lambdav2(name, code_path, handler, runtime="python310", role=None, environment={}, template=None, topic=None, s3_bucket=None, min_instance=1, max_instance=3, ram="256M", timeout_seconds=60, imports=None, gcp_config=None, opts=None):
    """
    Create a Cloud Function v2.

    Parameters
    ----------
    code_path: of business logic
    name: of serverless function
    handler: of serverless function
    role: IAM role of serverless function
    environment: environment variables of serverless function
    template: of serverless function
    topic: of Message Queue (pubsub)
    min_instance: of serverless functions
    max_instance: oof serverless function
    ram: of serverless function
    timeout_seconds: max duration of serverless function
    runtime: of serverless function
    imports: required by serverless function
    gcp_config: store GCP configuration
    opts: of Pulumi

    Returns Cloud Function
    -------

    """
    # Put code into a Cloud Storage bucket and make an object for serverless function.
    bucket = gcp_config["code_bucket"]
    bucket_object = create_bucket_object(f"{name}-object", bucket, f"./serverless_code/output/gcp/{code_path}/")
    event_trigger = event_trigger_config(template, topic)
    if template.startswith("s3"):
        event_trigger = s3_notification(name, s3_bucket, gcp_config, opts)
    # Serverless function
    runtime = runtime.replace(".", "")
    function = Function(name,
                        name=name,
                        location=region,
                        project=project,
                        build_config=FunctionBuildConfigArgs(
                            runtime=runtime,
                            entry_point="template",
                            environment_variables={
                                "GOOGLE_FUNCTION_SOURCE": handler.split(".")[0] + get_file_extension(runtime)
                            },
                            source=FunctionBuildConfigSourceArgs(
                                storage_source=FunctionBuildConfigSourceStorageSourceArgs(
                                    bucket=bucket.name,
                                    object=bucket_object.name,
                                ),
                            ),
                        ),
                        service_config=FunctionServiceConfigArgs(
                            max_instance_count=max_instance,
                            min_instance_count=min_instance,
                            available_memory=str(ram) + "M",
                            timeout_seconds=timeout_seconds,
                            environment_variables=environment,
                            # ingress_settings="ALLOW_INTERNAL_ONLY", # TODO: needed?
                            all_traffic_on_latest_revision=True,
                        ),
                        event_trigger=event_trigger,
                        opts=opts
                        )

    # IAM role of serverless function
    invoker = FunctionIamMember(f"{name}-invoker",
                                project=function.project,
                                location=function.location,
                                cloud_function=function.name,
                                role=role,
                                member="allUsers"
                                )
    return function


def event_trigger_config(template, topic):
    """
    Create an event trigger for serverless functions.

    Parameters
    ----------
    template: of serverless function
    topic: of message queue that will trigger serevrless function

    Returns None if http triggered else FunctionEventTrigger for message queue
    -------

    """
    if template.startswith("http"):
        return None
    elif template.startswith("mq"):
        return FunctionEventTriggerArgs(
            trigger_region=region,
            event_type="google.cloud.pubsub.topic.v1.messagePublished",
            pubsub_topic=Output.concat("projects/", project, "/topics/", topic.name),
            retry_policy="RETRY_POLICY_DO_NOT_RETRY",  # TODO: offer as parameter
        )


def s3_notification(name, bucket, gcp_config, opts=None):
    message_queue, message_queue_environment = create_pubsub(f"{name}-s3-notification", opts=opts)
    event_trigger = event_trigger_config("mq", message_queue)

    binding = TopicIAMBinding(f"{name}-binding-s3-notification",
                              topic=message_queue.id,
                              role="roles/pubsub.publisher",
                              members=[f"serviceAccount:{gcp_config['service_account'].email_address}"]
                              )
    notification = Notification(f"{name}-s3-notification",
                                bucket=bucket[0] if isinstance(bucket[0], str) else bucket[0].name,
                                payload_format="JSON_API_V1",
                                topic=message_queue.id,
                                event_types=["OBJECT_FINALIZE"],
                                opts=merge_opts(opts, ResourceOptions(depends_on=[binding]))
                                )
    return event_trigger


def get_file_extension(runtime: str):
    """
    Find file extensions to find business logic code.

    Parameters
    ----------
    runtime: of serverless function

    Returns file extension
    -------

    """
    if runtime.startswith("python"):
        return ".py"
