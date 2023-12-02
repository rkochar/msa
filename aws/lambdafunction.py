from pulumi import AssetArchive, FileArchive
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, EventSourceMapping


def create_lambda(name, handler, role, environment, template, http_trigger=True, sqs=None, sqldb=None, ram=256, runtime="python3.10", timeout_seconds=60, aws_config=None, opts=None):
    """
    Create Lambda (faas).

    If Lambda is triggered by MQ, AWS requires SQS url in environment.

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
    vpc, _, subnet_group, _ = aws_config
    handler = handler.replace(".", "-") + ".template"

    vpc_config = None if "sql" not in template else {
        "security_group_ids": [vpc.default_security_group_id],
        "subnet_ids": subnet_group.subnet_ids
    }

    lambda_function = Function(name,
                               runtime=runtime,
                               code=AssetArchive({
                                   '.': FileArchive(f'./code/output/aws/')
                               }),
                               timeout=timeout_seconds,
                               handler=handler,
                               role=role.arn,
                               environment=FunctionEnvironmentArgs(
                                   variables=environment
                                   ),
                               memory_size=ram,
                               vpc_config=vpc_config,
                               opts=opts
                               )
    if template.startswith("mq"):
        mapping = EventSourceMapping(f"{name}-event-trigger",
                                     event_source_arn=sqs.arn,
                                     function_name=lambda_function.arn
                                     )
    return lambda_function
