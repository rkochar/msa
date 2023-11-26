from google.cloud import pubsub_v1
from os import getenv
import functions_framework


@functions_framework.http
def template(request):
    query_string_parameters = request.args
    headers = request.headers

    topic_path = getenv("TOPIC_ID")
    publisher = pubsub_v1.PublisherClient()

    body = ""

    future = publisher.publish(topic_path, bytes(body, "utf-8"))
    return future.result()
