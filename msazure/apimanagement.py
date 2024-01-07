from pulumi_azure.apimanagement import Api, ApiImportArgs
from pulumi import export
from msazure.service import create_service

import oyaml as yaml

def create_apigw(name, routes, msazure_config, opts):
    resource_group_name = msazure_config.get("resource_group_name")
    service = create_service(name, msazure_config)
    parse_routes(routes)

    api = Api(f"{name}-apim",
              resource_group_name=resource_group_name,
              api_management_name=service.name,
              display_name=f"{name} APIGW",
              revision=1,
              path=name,
              protocols=["https"],
              service_url=f"https://{name}-faas-monad.azurewebsites.net",
              import_=ApiImportArgs(
                  content_format="openapi",
                  content_value=open("./msazure/editor.yaml").read()
                  #content_format="openapi",
                  #content_value=open("./msazure/apiconfig.yaml").read(),
                  ),
              subscription_required=False,
              opts=opts
              )

    return api

def parse_routes(routes):
    with open("./gcp/apiconfigtemplate.yaml") as f:
        apiconfig = yaml.full_load(f)
    f.close()

    print(f"api config: {apiconfig}")

    for route in routes:
        if apiconfig["paths"] is None:
            apiconfig["paths"] = {}
        apiconfig["paths"][route[0]] = {}
        apiconfig["paths"][route[0]][route[1].lower()] = {"summary": route[4],
                                                          "operationId": route[0],
                                                          "x-azure-api-id": {
                                                              "address": f"https://{route[3]}.azurewebsites.net/api{route[0]}"
                                                          },
                                                          "responses": {"200": {"description": "TODO",
                                                                                "schema": {"type": "string"}}}}
    with open("./msazure/apiconfig.yaml", "w") as f:
        yaml.dump(apiconfig, f)
    f.close()


# curl -d "" -X POST https://foobar-apim-service.azure-api.net/foobar-foo/foo -H "Ocp-Apim-Subscription-Key: <key>"
