from pulumi_gcp.cloudfunctions import Function, FunctionIamMember
from pulumi import Config, export

config = Config("gcp")
region = config.get("region")


def create_lambda(name, handler, role, environment, source_bucket, bucket_archive, runtime="python310", opts=None):
    function = Function(name,
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
    invoker = FunctionIamMember(f"{name}-invoker",
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
