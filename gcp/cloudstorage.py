from pulumi_gcp.storage import Bucket, BucketObject
from pulumi import FileAsset, FileArchive, Config

config = Config("gcp")
region = config.require("region")


def create_bucket(name):
    """
    Create Cloud Storage bucket.

    Parameters
    ----------
    name: of the bucket

    Returns Cloud Storage bucket
    -------

    """
    return Bucket(name, location=region)


def create_bucket_object(name, bucket, path):
    """
    Create Cloud Storage bucket object.

    Parameters
    ----------
    name: of cloud storage bucket object
    bucket: cloud storage bucket to make object in
    path: in local machine to FileArchive and make a bucket object

    Returns Cloud Storage bucket object
    -------

    """
    return BucketObject(name,
                        bucket=bucket.name,
                        source=FileArchive(path))
