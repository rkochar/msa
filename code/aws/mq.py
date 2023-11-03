import boto3
import os


def hello_pubsub(event, context):
    sqs = boto3.client('sqs')
    queue_url = os.environ['SQS_transaction']

    message = event.get("Records")[0]
    print(f"Body: {message.get('body')}")

    receipt_handle = message.get('receiptHandle')

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % message)

