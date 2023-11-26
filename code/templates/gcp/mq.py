import base64
import functions_framework


@functions_framework.cloud_event
def template(cloud_event):
    message = base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8")

    body = ""
