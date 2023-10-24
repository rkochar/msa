from pulumi import AssetArchive, FileArchive
from pulumi_aws import lambda_

def create_lambda(name, handlerfile, handlerfunc, role, runtime="python3.10", timeout=60):
    return lambda_.Function(name,
                            runtime=runtime,
                            code=AssetArchive({
                                '.': FileArchive('./code')
                            }),
                            timeout=timeout,
                            handler=f"{handlerfile}.{handlerfunc}",
                            role=role.arn
                            )
