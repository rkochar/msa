import pulumi_gcp.cloudfunctions as v1
from pulumi_gcp.cloudfunctionsv2 import Function, FunctionIamMember, FunctionBuildConfigArgs, \
    FunctionBuildConfigSourceArgs, FunctionBuildConfigSourceStorageSourceArgs, FunctionServiceConfigArgs, \
    FunctionEventTriggerArgs, FunctionEventTriggerEventFilterArgs
from pulumi import Config, export, Output

config = Config("gcp")
region = config.get("region")
project = config.get("project")


def create_lambdav2(name, handler, role, environment, http_trigger, topic, source_bucket, bucket_archive,
                    min_instance=1, max_instance=3,
                    ram="256M", timeout_seconds=60, runtime="python310", opts=None):
    function = Function(name,
                        name=name,
                        location=region,
                        project="master-thesis-faas-monad",  # project,
                        build_config=FunctionBuildConfigArgs(
                            runtime=runtime,
                            entry_point=handler[1],
                            environment_variables={
                                "GOOGLE_FUNCTION_SOURCE": str(handler[0]) + get_file_extension(runtime)
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
                        opts=opts
                        )
    invoker = FunctionIamMember(f"{name}-invoker",
                                project=function.project,
                                location=function.location,
                                cloud_function=function.name,
                                role=role,
                                member="allUsers"
                                )
    export(f'lambda-{name}-url', function.url)
    return function


def event_trigger_config(http_trigger, topic):
    if http_trigger:
        return None
    else:
        return FunctionEventTriggerArgs(
            trigger_region=region,
            event_type="google.cloud.pubsub.topic.v1.messagePublished",
            pubsub_topic=Output.concat("projects/", project, "/topics/", topic.name),
            # topic, # topic: "projects/master-thesis-faas-monad/topics/test-topic"
            retry_policy="RETRY_POLICY_DO_NOT_RETRY",  # TODO: offer as parameter
            # event_filters=[FunctionEventTriggerEventFilterArgs(
            #    attribute="bucket",
            #    value=trigger_bucket.name,
            # )],
        )


def create_lambda(name, handler, role, environment, source_bucket, bucket_archive, runtime="python310", opts=None):
    function = v1.Function(name,
                           name=name,
                           runtime=runtime,
                           region=region,
                           environment_variables=environment,
                           build_environment_variables={
                               "GOOGLE_FUNCTION_SOURCE": str(handler[0]) + get_file_extension(runtime)
                           },
                           source_archive_bucket=source_bucket.name,
                           source_archive_object=bucket_archive.name,
                           entry_point=handler[1],
                           trigger_http=True,
                           opts=opts
                           )
    invoker = v1.FunctionIamMember(f"{name}-invoker",
                                   project=function.project,
                                   region=function.region,
                                   cloud_function=function.name,
                                   role=role,
                                   member="allUsers"
                                   )
    export(f'lambda-{name}-url', function.https_trigger_url)
    return function


def get_file_extension(runtime: str):
    if runtime.startswith("python"):
        return ".py"
