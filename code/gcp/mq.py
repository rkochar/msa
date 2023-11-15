import base64
import functions_framework


@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    print(str(base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")))
