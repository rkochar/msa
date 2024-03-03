import resource
from time import time
def template(event, context):
    name = ""
    <start-time>
    <start-span>
    parent_span = None

    body = ""

    <end-time>
    <end-span>

    return {
        "statusCode": 200,
        "body": json.dumps({"body": body,})
    }
