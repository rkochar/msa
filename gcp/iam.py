from pulumi_gcp import cloudfunctionsv2

import pulumi
import pulumi_gcp as gcp


def create_iam_role(name):
    pass

# source_bucket = gcp.storage.Bucket("source-bucket",
#     location="US",
#     uniform_bucket_level_access=True)
# object = gcp.storage.BucketObject("object",
#     bucket=source_bucket.name,
#     source=pulumi.FileAsset("function-source.zip"))
# # Add path to the zipped function source code
# trigger_bucket = gcp.storage.Bucket("trigger-bucket",
#     location="us-central1",
#     uniform_bucket_level_access=True)
# gcs_account = gcp.storage.get_project_service_account()
# # To use GCS CloudEvent triggers, the GCS service account requires the Pub/Sub Publisher(roles/pubsub.publisher) IAM role in the specified project.
# # (See https://cloud.google.com/eventarc/docs/run/quickstart-storage#before-you-begin)
# gcs_pubsub_publishing = gcp.projects.IAMMember("gcs-pubsub-publishing",
#     project="my-project-name",
#     role="roles/pubsub.publisher",
#     member=f"serviceAccount:{gcs_account.email_address}")
# account = gcp.service_account.Account("account",
#     account_id="gcf-sa",
#     display_name="Test Service Account - used for both the cloud function and eventarc trigger in the test")
# # Permissions on the service account used by the function and Eventarc trigger
# invoking = gcp.projects.IAMMember("invoking",
#     project="my-project-name",
#     role="roles/run.invoker",
#     member=account.email.apply(lambda email: f"serviceAccount:{email}"),
#     opts=pulumi.ResourceOptions(depends_on=[gcs_pubsub_publishing]))
# event_receiving = gcp.projects.IAMMember("event-receiving",
#     project="my-project-name",
#     role="roles/eventarc.eventReceiver",
#     member=account.email.apply(lambda email: f"serviceAccount:{email}"),
#     opts=pulumi.ResourceOptions(depends_on=[invoking]))
# artifactregistry_reader = gcp.projects.IAMMember("artifactregistry-reader",
#     project="my-project-name",
#     role="roles/artifactregistry.reader",
#     member=account.email.apply(lambda email: f"serviceAccount:{email}"),
#     opts=pulumi.ResourceOptions(depends_on=[event_receiving]))
# function = gcp.cloudfunctionsv2.Function("function",
#     location="us-central1",
#     description="a new function",
#     build_config=gcp.cloudfunctionsv2.FunctionBuildConfigArgs(
#         runtime="nodejs12",
#         entry_point="entryPoint",
#         environment_variables={
#             "BUILD_CONFIG_TEST": "build_test",
#         },
#         source=gcp.cloudfunctionsv2.FunctionBuildConfigSourceArgs(
#             storage_source=gcp.cloudfunctionsv2.FunctionBuildConfigSourceStorageSourceArgs(
#                 bucket=source_bucket.name,
#                 object=object.name,
#             ),
#         ),
#     ),
#     service_config=gcp.cloudfunctionsv2.FunctionServiceConfigArgs(
#         max_instance_count=3,
#         min_instance_count=1,
#         available_memory="256M",
#         timeout_seconds=60,
#         environment_variables={
#             "SERVICE_CONFIG_TEST": "config_test",
#         },
#         ingress_settings="ALLOW_INTERNAL_ONLY",
#         all_traffic_on_latest_revision=True,
#         service_account_email=account.email,
#     ),
#     event_trigger=gcp.cloudfunctionsv2.FunctionEventTriggerArgs(
#         trigger_region="us-central1",
#         event_type="google.cloud.storage.object.v1.finalized",
#         retry_policy="RETRY_POLICY_RETRY",
#         service_account_email=account.email,
#         event_filters=[gcp.cloudfunctionsv2.FunctionEventTriggerEventFilterArgs(
#             attribute="bucket",
#             value=trigger_bucket.name,
#         )],
#     ),
#     opts=pulumi.ResourceOptions(depends_on=[
#             event_receiving,
#             artifactregistry_reader,
#         ]))