from datetime import datetime, timedelta, timezone


def publish_message(message, publish=False):
    if not publish:
        return message
    print(f"publish_message: {message}")

    queue_name, regex = getenv('QUEUE_NAME'), getenv("REGEX")
    queue_url = getenv("SQS_DO_NOT_USE") if regex == "true" else getenv(f"SQS_{queue_name}")
    sqs, output = boto3.client('sqs'), []

    output.append(put_message_in_queue(message, sqs, queue_name, queue_url))

    return {
        'statusCode': 200,
        'body': str(output)
    }


def put_message_in_queue(message, sqs, queue_name, queue_url):
    dedup_time = str(datetime.now(timezone(timedelta(hours=2))))
    dedupid = re.sub(pattern=r'\W+', repl='', string=dedup_time)

    print(f"Publishing message: {message} to queue: {queue_name}")

    if queue_url.endswith("fifo"):
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=message, MessageGroupId=queue_name,
                                    MessageDeduplicationId=dedupid)
    else:
        response = sqs.send_message(QueueUrl=queue_url, MessageBody=message)
    return f'Publish response for message: {message} in group {queue_name} is: {response}'