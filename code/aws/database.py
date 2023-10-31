import boto3
import json


def database(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps("hello database")
    }