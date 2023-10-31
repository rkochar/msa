from gcp import cloudstorage as gcp_cs
from pulumi_gcp import Provider
from pulumi import ResourceOptions


def setup_gcp():
    google_provider = ResourceOptions(provider=Provider("google-beta"))
    bucket = gcp_cs.create_bucket("lambda-bucket")
    code_object = gcp_cs.add_object("lambda-code-archive", bucket, "./code/gcp/")

    return google_provider, bucket, code_object