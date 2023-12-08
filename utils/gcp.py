from gcp import cloudstorage as gcp_cs
from pulumi_gcp import Provider
from pulumi import ResourceOptions


def setup_gcp():
    google_provider = ResourceOptions(provider=Provider("google-beta"))
    code_bucket = gcp_cs.create_bucket("code-bucket")

    return {"google_provider": google_provider,
            "code_bucket": code_bucket
            }

