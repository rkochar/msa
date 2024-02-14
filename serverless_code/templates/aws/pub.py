from datetime import datetime, timedelta, timezone


def publish_message(message):
    queue_name, regex = getenv('QUEUE_NAME'), getenv("REGEX")
    queue_url = getenv("SQS_DO_NOT_USE") if regex else getenv(f"SQS_{queue_name}")

    dedup_time = str(datetime.now(timezone(timedelta(hours=2))))
    dedupid = re.sub(pattern=r'\W+', repl='', string=dedup_time)

    print(f"Publishing message: {message} to queue: {queue_name}")
    sqs = boto3.client('sqs')
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=message, MessageGroupId=queue_name, MessageDeduplicationId=dedupid)
    output = f'Publish response for message: {message} in group {queue_name} is: {response}'
    return {
        'statusCode': 200,
        'body': output
    }
