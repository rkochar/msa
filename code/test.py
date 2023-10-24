import json

def lambda_handler(event, context):
    # print(f"event: {event}") # message
    # print(f"context: {context}") # log stream etc
    return {
        "statusCode": 200,
        "body": json.dumps(f"Hello tester!")
    }


def apigw_test_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps(f"Hello apigw tester!")
    }
