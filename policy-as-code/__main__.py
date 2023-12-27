from pulumi_policy import (
    EnforcementLevel,
    PolicyPack,
    ReportViolation,
    ResourceValidationArgs,
    ResourceValidationPolicy,
)

from pulumi import Config

config = Config()
cloud_provider = config.get("cloud_provider")


def aws_s3_no_public_read_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if "aws:s3/bucketV2:BucketV2" in args.resource_type and "acl" in args.props:
        acl = args.props["acl"]
        if acl == "public-read" or acl == "public-read-write":
            report_violation(
                "You cannot set public-read or public-read-write on an S3 bucket.")


def gcp_storage_bucket_no_public_read_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if args.resource_type == "gcp:storage/bucketACL:BucketACL" and "predefinedAcl" in args.props:
        acl = args.props["predefinedAcl"]
        if acl == "public-read" or acl == "public-read-write":
            report_violation("Storage buckets acl cannot be set to public-read or public-read-write.")


def azure_storage_container_no_public_read_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    if args.resource_type == "azure:storage/container:Container" and "containerAccessType" in args.props:
        access_type = args.props["containerAccessType"]
        if access_type == "blob" or access_type == "container":
            report_violation(
                "Azure Storage Container must not have blob or container access set. " +
                "Read more about read access here: " +
                "https://docs.microsoft.com/en-us/azure/storage/blobs/storage-manage-access-to-resources")


def storage_bucket_no_public_read_validator(args: ResourceValidationArgs, report_violation: ReportViolation):
    match cloud_provider:
        case "aws":
            return aws_s3_no_public_read_validator
        case "gcp":
            return gcp_storage_bucket_no_public_read_validator
        case "azure":
            return azure_storage_container_no_public_read_validator


storage_bucket_no_public_read = ResourceValidationPolicy(
    name=f"{cloud_provider}-storage-bucket-no-public-read",
    description=f"Prohibits setting the publicRead or publicReadWrite permission on {cloud_provider} storage buckets.",
    validate=storage_bucket_no_public_read_validator,
)

PolicyPack(
    name="storage-buckets-no-public-read",
    enforcement_level=EnforcementLevel.MANDATORY,
    policies=[
        storage_bucket_no_public_read,
    ],
)
