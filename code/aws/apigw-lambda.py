import json
import datetime
import functions_framework


def foo(event, context):
    sender = event.get("headers").get("sender")
    receiver = event.get("headers").get("receiver")
    amount = event.get("headers").get("amount")

    return {
        "statusCode": 200,
        "body": json.dumps(f"hello foo. sender: {sender}, receiver: {receiver}, amount: {amount}")
    }


def bar(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(f"Time is {datetime.datetime.now()}")
    }


def z(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps("hello z")
    }
