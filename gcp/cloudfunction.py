from pulumi_gcp.cloudfunctionsv2 import Function, FunctionIamMember, FunctionBuildConfigArgs, \
    FunctionBuildConfigSourceArgs, FunctionBuildConfigSourceStorageSourceArgs, FunctionServiceConfigArgs, \
    FunctionEventTriggerArgs
from pulumi import Config, Output

config = Config("gcp")
region = config.get("region")
project = config.get("project")


def create_lambdav2(name, handler, role, environment, http_trigger, topic, source_bucket, bucket_archive,
                    min_instance=1, max_instance=3,
                    ram="256M", timeout_seconds=60, runtime="python310", imports=None, opts=None):
    function = Function(name,
                        name=name,
                        location=region,
                        project=project,
                        build_config=FunctionBuildConfigArgs(
                            runtime=runtime,
                            entry_point="template",
                            environment_variables={
                                "GOOGLE_FUNCTION_SOURCE": handler.replace(".", "-") + get_file_extension(runtime)
                            },
                            source=FunctionBuildConfigSourceArgs(
                                storage_source=FunctionBuildConfigSourceStorageSourceArgs(
                                    bucket=source_bucket.name,
                                    object=bucket_archive.name,
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
                        event_trigger=event_trigger_config(http_trigger, topic),
                        opts=opts  # TODO: Put code archive in depends_on
                        )
    invoker = FunctionIamMember(f"{name}-invoker",
                                project=function.project,
                                location=function.location,
                                cloud_function=function.name,
                                role=role,
                                member="allUsers"
                                )
    return function


def event_trigger_config(http_trigger, topic):
    if http_trigger:
        return None
    else:
        return FunctionEventTriggerArgs(
            trigger_region=region,
            event_type="google.cloud.pubsub.topic.v1.messagePublished",
            pubsub_topic=Output.concat("projects/", project, "/topics/", topic.name),
            retry_policy="RETRY_POLICY_DO_NOT_RETRY",  # TODO: offer as parameter
        )


def get_file_extension(runtime: str):
    if runtime.startswith("python"):
        return ".py"
