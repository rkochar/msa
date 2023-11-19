from pulumi_azure.apimanagement import Service

from pulumi import export

def create_service(name, azure_config, publisher_name="rahulkochar", publisher_email="rkochar9@gmail.com"):
    resource_group, storage_account, storage_container, app_service_plan = azure_config
    service = Service(name,
                      resource_group_name=resource_group.name,
                      location=resource_group.location,
                      publisher_name=publisher_name,
                      publisher_email=publisher_email,
                      sku_name="Developer_1",
                      )

    export("service_url", service.portal_url)
    export("gateway_url", service.gateway_url)
    export("gateway_regional_url", service.gateway_regional_url)
    export("management_api_url", service.management_api_url)
    export("developer_portal_url", service.developer_portal_url)
    export("public_ip_addresses", service.public_ip_addresses)
    export("portal_url", service.portal_url)
    return service

