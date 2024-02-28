from gcp import cloudstorage as gcp_cs
from pulumi_gcp import Provider
from pulumi_gcp.storage import get_project_service_account
from pulumi import ResourceOptions


def setup_gcp():
    google_provider = ResourceOptions(provider=Provider("google-beta"))
    code_bucket = gcp_cs.create_bucket("serverless-code-bucket")
    service_account = get_project_service_account()


    return {
        "google_provider": google_provider,
        "code_bucket": code_bucket,
        "service_account": service_account
    }
