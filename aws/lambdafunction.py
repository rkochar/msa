from pulumi import AssetArchive, FileArchive
from pulumi_aws.lambda_ import Function, FunctionEnvironmentArgs


def create_lambda(name, handler, role, environment, runtime="python3.10", timeout=60, project="", opts=None):
    return Function(name,
                    runtime=runtime,
                    code=AssetArchive({
                        '.': FileArchive(f'./code{project}')
                    }),
                    timeout=timeout,
                    handler=handler,
                    role=role.arn,
                    environment=FunctionEnvironmentArgs(
                        variables=environment
                        ),
                    opts=opts
                    )
