from base64 import b64encode
import oyaml as yaml

from pulumi import Config, ResourceOptions
import pulumi_gcp as gcp

config = Config("gcp")
project = config.require("project")
region = config.get("region")


def create_apigw(name, routes, opts=None):
    apigw = gcp.apigateway.Api(name, api_id=f"apigw-id-{name}", opts=opts)
    # opts = ResourceOptions(provider="google_beta")
    parse_routes(routes)
    api_config = create_api_config(apigw, opts=opts)
    gateway = create_api_gateway(name, api_config, opts=opts)
    return apigw


def create_api_config(apigw, opts=None):
    return gcp.apigateway.ApiConfig("apiCfgApiConfig",
                                    api=apigw.api_id,
                                    api_config_id="my-config",
                                    openapi_documents=[gcp.apigateway.ApiConfigOpenapiDocumentArgs(
                                        document=gcp.apigateway.ApiConfigOpenapiDocumentDocumentArgs(
                                            path="spec.yaml",
                                            contents=(lambda path: b64encode(
                                                open(path).read().encode()).decode())(
                                                "./gcp/apiconfig.yaml")
                                        ),
                                    )],
                                    opts=ResourceOptions(provider="google_beta"))


def create_api_gateway(name, api_config, opts=None):
    return gcp.apigateway.Gateway("apiGwGateway",
                                  api_config=api_config.id,
                                  gateway_id=f"api-gateway-{name}",
                                  opts=ResourceOptions(provider="google_beta"))


def parse_routes(routes):
    with open("./gcp/apiconfigtemplate.yaml") as f:
        apiconfig = yaml.full_load(f)
    f.close()

    for route in routes:
        if apiconfig["paths"] is None:
            apiconfig["paths"] = {}
        apiconfig["paths"][route[0]] = {}
        apiconfig["paths"][route[0]][route[1].lower()] = {"summary": route[2],
                                                          "operationId": route[0],
                                                          "x-google-backend": {
                                                              "address": f"https://{region}-{project}.cloudfunctions.net{route[0]}"},
                                                          "responses": {"200": {"description": "TODO",
                                                                                "schema": {"type": "string"}}}}

        with open("./gcp/apiconfig.yaml", "w") as f:
            yaml.dump(apiconfig, f, indent=2)
        f.close()


if __name__ == "__main__":
    parse_routes([("/", "GET", "apigw_lambda_foo"), ("/bar", "GET", "apigw_lambda_bar")])
