from pulumi_gcp.storage import Bucket, BucketObject
from pulumi import FileAsset, FileArchive, Config

config = Config("gcp")
region = config.require("region")


def create_bucket(name):
    return Bucket(name, location=region)


def create_bucket_object(name, bucket, path):
    return BucketObject(name,
                        bucket=bucket.name,
                        source=FileArchive(path))

