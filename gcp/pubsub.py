from pulumi_gcp import pubsub


def create_pubsub(topic_name, message_retention_seconds="60s", environment={}, opts=None):
    """
    Create message queue.

    Parameters
    ----------
    topic_name: of message queue
    message_retention_seconds: max duration a message is visible in the queue for
    environment: environment variables of serverless function to put connection information of message queue into
    opts: of Pulumi

    Returns Pubsub object (message queue) and environment variables of serverless function
    -------

    """
    # TODO: Add message_retention_duration, if feasible/needed. It is paid.
    topic = pubsub.Topic(topic_name,
                         name=topic_name,
                         # message_retention_duration=message_retention_seconds,
                         opts=opts)
    environment["TOPIC_ID"] = topic.id
    return topic, environment
