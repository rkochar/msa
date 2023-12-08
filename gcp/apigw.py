from base64 import b64encode
import oyaml as yaml
from utils.helpers import merge_opts

from pulumi import Config, export, Output, ResourceOptions
import pulumi_gcp as gcp


config = Config("gcp")
project = config.get("project")
region = config.get("region")


def create_apigw(name, routes, opts=None):
    apigw = gcp.apigateway.Api(name, api_id=f"apigw-id-{name}", project=project, opts=opts)
    api_config = create_api_config(name, apigw, routes=routes, opts=merge_opts(opts, ResourceOptions(depends_on=[apigw])))
    gateway = create_api_gateway(name, api_config, opts=merge_opts(opts, ResourceOptions(depends_on=[api_config])))

    export(f"apigw-url-{name}", Output.concat("https://", gateway.default_hostname))
    return apigw


def create_api_config(name, apigw, routes, opts=None):
    parse_routes(routes)
    return gcp.apigateway.ApiConfig(f"{name}-config",
                                    api=apigw.api_id,
                                    api_config_id="my-config",
                                    project=project,
                                    openapi_documents=[gcp.apigateway.ApiConfigOpenapiDocumentArgs(
                                        document=gcp.apigateway.ApiConfigOpenapiDocumentDocumentArgs(
                                            path="spec.yaml",
                                            contents=(lambda path: b64encode(open(path).read().encode()).decode())("./gcp/apiconfig.yaml"),
                                        ),
                                    )],
                                    opts=opts)


def create_api_gateway(name, api_config, opts=None):
    return gcp.apigateway.Gateway(f"{name}-gateway",
                                  project=project,
                                  region=region,
                                  api_config=api_config.id,
                                  gateway_id=f"api-gateway-{name}",
                                  opts=opts)


def parse_routes(routes):
    with open("./gcp/apiconfigtemplate.yaml") as f:
        apiconfig = yaml.full_load(f)
    f.close()

    for route in routes:
        if apiconfig["paths"] is None:
            apiconfig["paths"] = {}
        apiconfig["paths"][route[0]] = {}
        apiconfig["paths"][route[0]][route[1].lower()] = {"summary": route[4],
                                                          "operationId": route[0],
                                                          "x-google-backend": {
                                                              "address": f"https://{region}-{project}.cloudfunctions.net/{route[3]}"
                                                          },
                                                          "responses": {"200": {"description": "TODO",
                                                                                "schema": {"type": "string"}}}}
    with open("./gcp/apiconfig.yaml", "w") as f:
        yaml.dump(apiconfig, f)
    f.close()


if __name__ == "__main__":
    parse_routes([("/", "GET", "apigw_lambda_foo"), ("/bar", "GET", "apigw_lambda_bar")])
