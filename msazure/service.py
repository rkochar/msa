from pulumi_azure.apimanagement import Service

from pulumi import export, Config

config = Config("azure")
location = config.get("location")



def create_service(name, msazure_config, publisher_name="rahulkochar", publisher_email="rkochar9@gmail.com"):
    resource_group_name = msazure_config.get("resource_group_name")
    service = Service(f"{name}-apim-service",
                      name=f"{name}-apim-service",
                      resource_group_name=resource_group_name,
                      location=location,
                      publisher_name=publisher_name,
                      publisher_email=publisher_email,
                      sku_name="Developer_1",
                      )

    export("gateway_url", service.gateway_url)
    return service
