from pulumi_aws.s3 import BucketV2, BucketAclV2, BucketObjectv2, Bucket, BucketObject


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


def create_bucket_object(name, bucket, source=None, content=None, content_type=None, opts=None):
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
                          content=content,
                          content_type=content_type,
                          opts=opts
                          )


def create_bucket_legacy(name, force_destroy=True, opts=None):
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
    bucket = Bucket(name,
                    force_destroy=force_destroy,
                    opts=opts
                    )
    return bucket


def create_bucket_object_legacy(name, bucket, source=None, content=None, content_type=None, opts=None):
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
    object_name = f"bucket-object-root" if name == "/" else f"bucket-object-{name}"
    return BucketObject(object_name,
                        key=name,
                        bucket=bucket.id,
                        source=source,
                        content=content,
                        content_type=content_type,
                        opts=opts
                        )
