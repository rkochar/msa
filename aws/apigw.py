from pulumi import export
from pulumi_aws_apigateway import RestAPI, RouteArgs


def create_apigw(name, routes):
    apigw = RestAPI(name, routes=parse_routes(routes))
    export(f'apigw-{name}-url', apigw.url)
    return apigw


def parse_routes(routes):
    rs = []
    for route in routes:
        rs.append(RouteArgs(path=route[0], method=route[1], event_handler=route[2]))
    return rs
