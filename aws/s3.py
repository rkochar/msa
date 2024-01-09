from pulumi_aws.s3 import BucketV2, BucketAclV2, BucketObjectv2


def create_bucket(name, force_destroy=True, opts=None):
    """
    Create S3.

    Parameters
    ----------
    name: of S3
    force_destroy:
    opts: of Pulumi

    Returns
    -------

    """
    bucket = BucketV2(name,
                      force_destroy=force_destroy,
                      opts=opts
                      )
    return bucket


def create_bucket_object(name, bucket, source, opts=None):
    """
    Create S3 bucket object.

    Parameters
    ----------
    name: of S3 object
    bucket: to make S3 object in
    source: of content to put into object
    opts: of Pulumi

    Returns S3 bucket object
    -------

    """
    return BucketObjectv2(f"bucket-object-{name}",
                          key=name,
                          bucket=bucket.id,
                          source=source,
                          opts=opts
                          )
