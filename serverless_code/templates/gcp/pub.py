from google.cloud import pubsub_v1


def publish_message(message):
    topic_path = getenv("TOPIC_ID")
    publisher = pubsub_v1.PublisherClient()

    if isinstance(message, str):
        return put_message_in_queue(message, topic_path, publisher)
    else:
        results = []
        for m in message:
            results.append(put_message_in_queue(m, topic_path, publisher))
        return results


def put_message_in_queue(message, topic_path, publisher):
    print(f"Publishing message: {message} to topic: {topic_path}")
    future = publisher.publish(topic_path, bytes(message, "utf-8"))
    return future.result()