from google.cloud import storage

storage_client = storage.Client()


def write_to_s3(bucket, key, data):
    blob = storage_client.get_bucket(bucket).blob(key)
    blob.upload_from_string(data)


def get_from_s3(bucket, key):
    blob = storage_client.get_bucket(bucket).blob(key)
    return blob.download_as_string().decode('utf-8')


def list_objects_from_s3(bucket, prefix):
    bucket = get_all_objects_s3(bucket)
    return [blob for blob in bucket if blob.startswith(prefix)]


def get_all_objects_s3(bucket):
    return [blob.name for blob in storage_client.get_bucket(bucket).list_blobs()]


def filter_objects_s3(bucket, prefix):
    objects = list_objects_from_s3(bucket, prefix)
    bucket = storage_client.get_bucket(bucket)
    l = []
    for obj in objects:
        if not obj.endswith('/'):
            d = {"Name": obj, "Size": bucket.get_blob(obj).size}
            l.append(d)
    return l