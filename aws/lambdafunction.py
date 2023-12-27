from pulumi import AssetArchive, FileArchive, ResourceOptions, Config
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, EventSourceMapping, LayerVersion
from utils.helpers import bash_command
from aws.s3 import create_bucket_object

config = Config()


def create_lambda(code_path, name, handler, role, environment, template, http_trigger=True, sqs=None, sqldb=None,
                  ram=256, runtime="python3.10", timeout_seconds=60, aws_config=None, imports=[], opts=None):
    """
    Create Lambda (faas).

    If Lambda is triggered by MQ, AWS requires SQS url in environment.

    :param imports:
    :param code_path:
    :param name: of lambda
    :param handler: <python file>.<method name> that will be called when the Lambda is triggered
    :param role: IAM role of Lambda
    :param environment: environment variables available to Lambda
    :param template:
    :param http_trigger: is Lambda triggered by HTTP
    :param sqs: if http_trigger is False, SQS object that will trigger Lambda
    :param ram: available to Lambda
    :param runtime: Language and Version of code that will run in Lambda
    :param timeout_seconds: max time a Lambda can run for
    :param aws_config:
    :param opts: of Pulumi
    :return: Lambda object
    """
    architecture = config.get("architecture") or ("arm64" if imports else "x86_64")
    code_bucket = aws_config.get("code_bucket")
    dir = code_path.split("/")[0]
    handler = handler.split(".")[0] + ".template"
    zip_command = bash_command(name=f"zip-lambda-{name}", command=f"rm -rf {name}.zip && zip -r {name}.zip *", path=f"./code/output/aws/{code_path}/")
    bucket_object = create_bucket_object(f"{dir}/{name}", code_bucket, f"./code/output/aws/{code_path}/{name}.zip",
                                         opts=ResourceOptions(depends_on=[code_bucket, zip_command]))

    vpc_config = None if "sql" not in template else {
        "security_group_ids": [aws_config.get("vpc").default_security_group_id],
        "subnet_ids": aws_config.get("subnet_group").subnet_ids
    }

    lambda_layer = [create_import_layer(code_path, name, runtime, code_bucket, architecture).arn] if len(imports) > 0 else None

    lambda_function = Function(name,
                               runtime=runtime,
                               handler=handler,
                               role=role.arn,
                               environment=FunctionEnvironmentArgs(
                                   variables=environment
                               ),

                               s3_bucket=bucket_object.bucket,
                               s3_key=bucket_object.key,
                               s3_object_version=bucket_object.version_id,
                               layers=lambda_layer,

                               memory_size=ram,
                               timeout=timeout_seconds,
                               architectures=[architecture],
                               vpc_config=vpc_config,
                               opts=opts
                               )
    if template.startswith("mq"):
        mapping = EventSourceMapping(f"{name}-event-trigger",
                                     event_source_arn=sqs.arn,
                                     function_name=lambda_function.arn
                                     )
    return lambda_function


def create_import_layer(code_path, name, runtime, code_bucket, architecture):
    import_path = f"./code/output/aws/{code_path}"
    zip_file = f"{code_path.replace('/', '-')}-layer.zip"
    wheel_architecture = "aarch64" if architecture == "arm64" else "x86_64"
    layer_script = bash_command(name=f"create-layer-{name}",
                                command=f"rm -rf python && mkdir python && "
                                        f"{runtime} -m pip install --platform=manylinux_2_17_{wheel_architecture} --only-binary=:all: -r requirements.txt -t ./python --no-cache && "
                                        f"zip -r {zip_file} ./python/ ",
                                path=import_path
                                )
    layer_object = create_bucket_object(f"{code_path}-layer", code_bucket, f"{import_path}/{zip_file}",
                                        opts=ResourceOptions(depends_on=[layer_script, code_bucket]))
    return create_lambda_layer(code_path, name, runtime, layer_object)


def create_lambda_layer(code_path, name, runtime, layer_object):
    layer_name = code_path.replace('/', '-').replace('.', '-')
    lambda_layer = LayerVersion(f"lambda-layer-{name}",
                                compatible_runtimes=[runtime],
                                layer_name=f"lambda-layer-{layer_name}",

                                s3_bucket=layer_object.bucket,
                                s3_key=layer_object.key,
                                s3_object_version=layer_object.version_id
                                )
    return lambda_layer

