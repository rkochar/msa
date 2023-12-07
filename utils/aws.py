from aws.s3 import create_bucket


def setup_aws():
    code_bucket = create_bucket("code-bucket")
    return {"code_bucket": code_bucket}
