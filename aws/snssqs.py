from pulumi_aws import sns, sqs


def create_sns_topic(name, opts=None):
    return sns.Topic(name, fifo_topic=False, opts=opts)


def create_sqs(name, visibility_timeout_seconds=60, opts=None):
    return sqs.Queue(name, fifo_queue=False, visibility_timeout_seconds=visibility_timeout_seconds, opts=opts)
