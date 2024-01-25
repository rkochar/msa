from google.cloud import pubsub_v1


def publish_message(message):
    topic_path = getenv("TOPIC_ID")
    publisher = pubsub_v1.PublisherClient()

    print(f"Publishing message: {message} to topic: {topic_path}")
    future = publisher.publish(topic_path, bytes(message, "utf-8"))
    return future.result()
