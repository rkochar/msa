from google.cloud import logging
from datetime import datetime, timedelta


def test():
    # Instantiates a client
    client = logging.Client()

    # The name of the log to read from
    log_name = 'foobar-foo'  # replace with your log name

    # Retrieves a Cloud Logging handler based on the environment
    logger = client.logger(log_name)

    # Lists the most recent entries
    for entry in logger.list_entries(order_by=logging.DESCENDING, page_size=10):
        print(entry.timestamp.isoformat())  # timestamp of the log
        print(entry.payload)  # the log data


def read_cloud_function_logs():
    # Instantiates a client
    client = logging.Client()

    # The name of the log to read from
    log_name = 'foobar-foo'  # replace with your log name

    # Convert UTC time to RFC3339 format
    now = datetime.now()
    start_time = now - timedelta(minutes=10)
    print(f"now: {now}")
    print(f"start_time: {start_time}")

    # The filter expression timestamp >= "{start_time}"
    # resource_type = "cloud_function" resource.labels.function_name = "metric" resource.labels.region = "europe-west1"
    # Read logs of cloud function
    filter_str = f'timestamp >= "{start_time}" AND resource.type = "cloud_function" AND resource.labels.function_name = "metric" AND resource.labels.region = "europe-west1"'

    # List logs
    for entry in client.list_entries(filter_=filter_str):  # API call
        timestamp = entry.timestamp.isoformat()
        print(f'Timestamp: {timestamp} Text Payload: {entry.payload}')


if __name__ == "__main__":
    read_cloud_function_logs()
    test()
