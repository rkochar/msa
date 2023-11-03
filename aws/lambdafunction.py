from pulumi import AssetArchive, FileArchive
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs, EventSourceMapping


def create_lambda(name, handler, role, environment, http_trigger=True, sqs=None, ram=256, runtime="python3.10", timeout_seconds=60, opts=None):
    lambda_function = Function(name,
                               runtime=runtime,
                               code=AssetArchive({
                                   '.': FileArchive(f'./code/aws/')
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

