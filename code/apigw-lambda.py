import json


def foo(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps("hello foo")
    }


def bar(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps("hello bar")
    }


def z(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps("hello z")
    }
