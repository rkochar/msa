import base64
import functions_framework

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    print(str(base64.b64decode(cloud_event.data["message"]["data"])))
    print("First print: " + str(base64.b64decode(cloud_event.data["message"]["data"])))
    #data = cloud_event.data.get("message")["data"]
    #print(base64.b64decode(f"Message received: {data}"))

