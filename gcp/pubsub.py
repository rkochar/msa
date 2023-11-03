from pulumi_gcp import pubsub


def create_pubsub(topic_name, message_retention_seconds="60s", opts=None):
    # TODO: Add message_retention_duration, if feasible/needed. It is paid.
    topic = pubsub.Topic(topic_name,
                         name=topic_name,
                         # message_retention_duration=message_retention_seconds,
                         opts=opts)
    return topic
