from pulumi_azure.appservice import Plan, PlanSkuArgs
from pulumi_azure.core import ResourceGroup
from pulumi_azure.storage import Account, Container
from pulumi import Config, ResourceOptions, export

from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient


config = Config("azure")
location = config.get("location") or "West Europe"

subscription_id = "3d1cfa10-9d74-4a8a-983e-921695f9e20a"
resource_group_name = "resourcegroup"
storage_account_name = "storageaccountfaasmonad"


def setup_azure_console():
    resource_group_name = "resourcegroupconsole"
    storage_account_name = "storageaccfaasconsole"
    storage_container_name = "storagecontainerconsole"

    app_service_plan = Plan("appserviceplan",
                            name="appserviceplan",
                            resource_group_name=resource_group_name,
                            location=location,
                            kind="FunctionApp",
                            reserved=True,

                            sku=PlanSkuArgs(
                                # name="Y1",
                                tier="Dynamic",
                                size="Y1",
                                # family="Y",
                                # capacity=0
                            ),
                            opts=ResourceOptions(protect=False)
                            )
    return {
        "app_service_plan": app_service_plan,
        "resource_group_name": resource_group_name,
        "storage_account_name": storage_account_name,
        "storage_container_name": storage_container_name
        }

def setup_azure():
    resource_group = ResourceGroup(resource_group_name,
                                   name=resource_group_name,
                                   location=location,
                                   opts=ResourceOptions(protect=False)
                                   )

    storage_account = Account(storage_account_name,
                              name=storage_account_name,
                              resource_group_name=resource_group.name,
                              location=resource_group.location,
                              account_tier="Standard",
                              account_replication_type="LRS",
                              opts=ResourceOptions(protect=False)
                              )

    storage_container = Container("storagecontainer",
                                  name="storagecontainer",
                                  storage_account_name=storage_account.name,
                                  container_access_type="private",
                                  opts=ResourceOptions(protect=False)
                                  )

    app_service_plan = Plan("appserviceplan",
                            name="appserviceplan",
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
                            ),
                            opts=ResourceOptions(protect=False)
                            )
    export("resource_group_name", resource_group.name)
    export("storage_account_name", storage_account.name)
    export("storage_account_primary_key", storage_account.primary_access_key)
    export("storage_account_connection_string", storage_account.primary_connection_string)
    export("app_service_plan_id", app_service_plan.id)
    export("location", resource_group.location)


    return {"resource_group": resource_group,
            "storage_account": storage_account,
            "storage_container": storage_container,
            "app_service_plan": app_service_plan,
            #"storage_account_connection_url" :get_storage_account_connection_url()
            }


def get_storage_account_connection_url():
    credential = DefaultAzureCredential()
    storage_client = StorageManagementClient(credential, subscription_id)
    storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)

    keys = storage_client.storage_accounts.list_keys(resource_group_name, storage_account_name)
    key = keys.keys[0].value
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={key};EndpointSuffix=core.windows.net"
    print(f"storage_conncetion_string: {connection_string}")
