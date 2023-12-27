from pulumi_aws.s3 import BucketV2, BucketAclV2, BucketObjectv2


def create_bucket(name, force_destroy=True, opts=None):
    bucket = BucketV2(name,
                      force_destroy=force_destroy,
                      opts=opts
                      )
    return bucket


def create_bucket_object(name, bucket, source, opts=None):
    return BucketObjectv2(f"bucket-object-{name}",
                          key=name,
                          bucket=bucket.id,
                          source=source,
                          opts=opts
                          )
