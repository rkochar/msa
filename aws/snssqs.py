from pulumi_aws import sns, sqs


def create_sns_topic(name, opts=None):
    return sns.Topic(name, fifo_topic=False, opts=opts)


def create_sqs(name, visibility_timeout_seconds=60, environment={}, opts=None):
    queue = sqs.Queue(name, name=name, fifo_queue=False, visibility_timeout_seconds=visibility_timeout_seconds, opts=opts)
    environment[f"SQS_{name}"] = queue.url
    return queue, environment
