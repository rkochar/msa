import boto3
import os


def template(event, context):
    sqs = boto3.client('sqs')
    queue_url = os.environ['SQS_']

    record = event.get("Records")[0]
    message = record.get('body')
    receipt_handle = record.get('receiptHandle')

    body = ""

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    print('Received and deleted message: %s' % record)
