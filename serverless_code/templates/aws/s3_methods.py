from boto3 import resource, client

# create an S3 session
s3 = resource('s3')
s3_client = client('s3')


def write_to_s3(bucket, key, data):
    print(f"Writing to s3://{bucket}/{key}")
    s3.Bucket(bucket).put_object(Key=key, Body=data)


def get_from_s3(bucket, key):
    return s3_client.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')


def list_objects_from_s3(bucket, prefix):
    return s3_client.list_objects(Bucket=bucket, Prefix=prefix)["Contents"]


def get_all_objects_s3(bucket):
    return s3.Bucket(bucket).objects.all()


def filter_objects_s3(bucket, prefix):
    return s3.Bucket(bucket).objects.filter(Prefix=prefix).all()
