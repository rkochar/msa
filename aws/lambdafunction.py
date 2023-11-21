from pulumi import AssetArchive, FileArchive
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, EventSourceMapping


def create_lambda(name, handler, role, environment, http_trigger=True, sqs=None, ram=256, runtime="python3.10", timeout_seconds=60, opts=None):
    """
    Create Lambda (faas).

    If Lambda is triggered by MQ, AWS requires SQS url in environment.

    :param name: of lambda
    :param handler: <python file>.<method name> that will be called when the Lambda is triggered
    :param role: IAM role of Lambda
    :param environment: environment variables available to Lambda
    :param http_trigger: is Lambda triggered by HTTP
    :param sqs: if http_trigger is False, SQS object that will trigger Lambda
    :param ram: available to Lambda
    :param runtime: Language and Version of code that will run in Lambda
    :param timeout_seconds: max time a Lambda can run for
    :param opts: of Pulumi
    :return: Lambda object
    """
    handler = handler.replace(".", "-") + ".template"
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
                               opts=opts
                               )
    if not http_trigger:
        mapping = EventSourceMapping(f"{name}-event-trigger",
                                     event_source_arn=sqs.arn,
                                     function_name=lambda_function.arn
                                     )
    return lambda_function

