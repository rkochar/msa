from pulumi_aws.sqs import Queue
from pulumi import export


def create_sqs(name, visibility_timeout_seconds=60, fifo=True, environment={}, opts=None):
    """
    Create SQS and add SQS url to environment that will be passed to Lambda so Lambda can poll MQ.

    :param name: of MQ
    :param visibility_timeout_seconds: time a message is visible for
    :param fifo: is sqs fifo
    :param environment: that will be passed to Lambda.
    :param opts: of Pulumi
    :return: SQS object
    """
    new_name = f"{name}.fifo" if fifo else name
    queue = Queue(new_name, name=new_name, fifo_queue=fifo, visibility_timeout_seconds=visibility_timeout_seconds,
                  opts=opts)
    environment[f"SQS_{name}"] = queue.url
    environment["QUEUE_NAME"] = name
    export(f"sqs-{name}-url", queue.url)
    return queue, environment
