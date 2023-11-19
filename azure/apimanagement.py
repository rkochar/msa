from pulumi_azure.apimanagement import Api
from pulumi import export
from azure.service import create_service

def create_apigw(name, routes, azure_config, opts):
    resource_group, storage_account, storage_container, app_service_plan = azure_config
    service = create_service(name, azure_config)
    api = Api(name,
              resource_group_name=resource_group.name,
              api_management_name=service.name,
              display_name=name,
              revision=1,
              path=name,
              protocols=["https", "http"],
              service_url="https://{}.azurewebsites.net".format(app_service_plan.name),
              opts=opts
              )

    return api
