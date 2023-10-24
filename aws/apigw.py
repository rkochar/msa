from pulumi import export
from pulumi_aws_apigateway import RestAPI

def create_apigw(name, routes):
    apigw = RestAPI('apigw', routes=parse_routes(routes))
    export('apigw-url', apigw.url)
    return apigw

def parse_routes(routes):
    rs = []
    for route in routes:
        rs.append(RouteArgs(path=route[0], method=route[1], event_handler=route[2]))
    return rs
