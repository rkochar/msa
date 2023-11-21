from pulumi_aws import sns, sqs


def create_sns_topic(name, opts=None):
    """
    Create SNS topic.

    :param name: of sns topic
    :param opts: of Pulumi
    :return: SNS Topic object
    """
    return sns.Topic(name, fifo_topic=False, opts=opts)


def create_sqs(name, visibility_timeout_seconds=60, environment={}, opts=None):
    """
    Create SQS and add SQS url to environment that will be passed to Lambda so Lambda can poll MQ.

    :param name: of MQ
    :param visibility_timeout_seconds: time a message is visible for
    :param environment: that will be passed to Lambda.
    :param opts: of Pulumi
    :return: SQS object
    """
    queue = sqs.Queue(name, name=name, fifo_queue=False, visibility_timeout_seconds=visibility_timeout_seconds, opts=opts)
    environment[f"SQS_{name}"] = queue.url
    return queue, environment
