from pulumi_azure.apimanagement import Api, ApiImportArgs
from pulumi import export
from msazure.service import create_service

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
              service_url=f"https://{name}-faas-monad.azurewebsites.net",
              #import_=ApiImportArgs(
              #    content_format="openapi",
              #    content_value=open("./serverless_code/output/msazure/apigw/openapi.json").read(),
              #    ),
              opts=opts
              )

    return api
