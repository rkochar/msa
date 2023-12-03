from aws.vpc import create_vpc
from aws.s3 import create_bucket


def setup_aws():
    code_bucket = create_bucket("code-bucket")
    vpc, subnet, subnet_group, vpc_endpoint = create_vpc("for-database-100")
    return code_bucket, vpc, subnet, subnet_group, vpc_endpoint
