import json
import datetime


def bar(event, context):
    sender = event.get("headers").get("sender")
    receiver = event.get("headers").get("receiver")
    amount = event.get("headers").get("amount")

    return {
        "statusCode": 200,
        "body": json.dumps(f"hello foo. sender: {sender}, receiver: {receiver}, amount: {amount}")
    }


def foo(event, context):
    query_string_params = event.get("queryStringParameters")
    name = "Lambda" if query_string_params is None else query_string_params.get("name")
    return {
        "statusCode": 200,
        "body": json.dumps(f"Time is {datetime.datetime.now()}. event: {name}")
    }

