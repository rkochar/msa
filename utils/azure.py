# from pulumi_azure_native.insights import Component, ApplicationType
# from pulumi_azure_native.web import WebApp, NameValuePairArgs, AppServicePlan, SkuDescriptionArgs, SiteConfigArgs
# from pulumi_azure_native.resources import ResourceGroup
# from pulumi_azure_native.storage import Blob, BlobType, Kind, SkuArgs, SkuName, StorageAccount, BlobContainer, PublicAccess

from pulumi_azure.appservice import Plan, PlanSkuArgs
from pulumi_azure.core import ResourceGroup
from pulumi_azure.storage import Account, Container
from pulumi import Config

config = Config("azure")
location = config.get("location") or "West Europe"


def setup_azure():
    resource_group = ResourceGroup('resourcegroup',
                                   location=location
                                   )

    storage_account = Account("storageaccount",
                              resource_group_name=resource_group.name,
                              location=resource_group.location,
                              account_tier="Standard",
                              account_replication_type="LRS"
                              )

    storage_container = Container("storagecontainer",
                                   storage_account_name=storage_account.name,
                                   container_access_type="private"
                                   )

    app_service_plan = Plan("appserviceplan",
                            resource_group_name=resource_group.name,
                            location=resource_group.location,
                            kind="FunctionApp",
                            reserved=True,

                            sku=PlanSkuArgs(
                                # name="Y1",
                                tier="Dynamic",
                                size="Y1",
                                # family="Y",
                                # capacity=0
                            )
                            )

    return resource_group, storage_account, storage_container, app_service_plan
