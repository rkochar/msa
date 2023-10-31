import boto3
import datetime
import json
from collections import deque
import os

sqs = boto3.client('sqs')
queue_url = os.environ.get("SQS_URL")
mvcc = {}


def consumer(event, context):
    print(f"QUEUE URL: {queue_url}")
    for i in range(12):
        mvcc[str(i)] = deque(maxlen=2)
        mvcc[str(i)].append((0, 10))

    sender = event.get("headers").get("sender")
    receiver = event.get("headers").get("receiver")
    amount = event.get("headers").get("amount")
    message_body = {"sender": sender, "receiver": receiver, "amount": amount}

    response = None
    if sender is not None and receiver is not None and amount is not None:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=str(message_body)
        )

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

# def update_mvcc(mvccdb, messages):
#     transactions = parse_kafka_message(messages)
#     # logging.info(f"Transactions accepted: {transactions} for MVCCDB: {mvccdb}")
#     for transaction in transactions:
#         mvccdb[transaction["sender"]].append(transaction["latest_version_sender"])
#         mvccdb[transaction["receiver"]].append(transaction["latest_version_receiver"])
#     #     logging.info(f"Transaction {transaction} written")
#     # logging.info(f"Finised writing: {transaction} to MVCCDB: {mvccdb}")
#     return mvccdb
#
#
# def process_transaction(mvccdb, transaction, write_producer):
#     # logging.info(f"Transaction received: {transaction}")
#     # logging.info(f"MVCCDB: {mvccdb}")
#     for t in transaction:
#         # logging.info(f"sender: {mvccdb[t['sender']][-1]}, amount: {t['amount']}")
#         if mvccdb[t["sender"]][-1][1] >= t["amount"]:
#             write_producer.publish_to_kafka(t)
#         # else:
#         #     logging.info(f"Transaction rejected: {t}")
#
#
# def consume_kafka_messages(mvccdb, transaction_consumer, update_consumer, write_producer):
#     # logging.info("Starting to consume messages")
#     while True:
#         messages = update_consumer.poll(timeout_ms=100)
#         if messages != {}:
#             mvccdb = update_mvcc(mvccdb, messages)
#         transaction = transaction_consumer.poll(timeout_ms=1000, max_records=1)
#         if transaction != {}:
#             process_transaction(mvccdb, parse_kafka_message(transaction), write_producer)