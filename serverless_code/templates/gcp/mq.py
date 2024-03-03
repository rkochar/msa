import base64
import functions_framework
from os import getenv
from time import time
from uuid import uuid4
from ast import literal_eval
import resource


@functions_framework.cloud_event
def template(cloud_event):
    name = ""
    <start-time>
    <start-span>
    print("starting")

    message = literal_eval(base64.b64decode(cloud_event.data["message"]["data"]).decode("utf-8"))
    print(f"Message from queue: {message}")
    parent_span = message.get('span') or {}

    if span is not None:
        span["span_depth"] = (parent_span.get('span_depth') or 0) + 1
        span["parent_span_id"] = parent_span.get('span_id')
        span["parent_name"] = parent_span.get('name')

    body = ""
    <end-time>

    if span is not None:
        <end-span>
        print(f"span: {span}")
