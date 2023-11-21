from pulumi import export
from pulumi_aws_apigateway import RestAPI, RouteArgs


def create_apigw(name, routes, opts=None):
    """
    API Gateway.

    :param name: of APIGW
    :param routes: map of path to lambda (see README.md for description of Route)
    :param opts: of Pulumi
    :return: apigw object
    """
    apigw = RestAPI(name, routes=parse_routes(routes), opts=opts)
    export(f'apigw-{name}-url', apigw.url)
    return apigw


def parse_routes(routes):
    """
    Parse routes into what AWS expects (remove extra fields added for other clouds).

    :param routes: List of Route
    :return: List of routes as expected by AWS APIGW.
    """
    rs = []
    for route in routes:
        rs.append(RouteArgs(path=route[0], method=route[1], event_handler=route[2]))
    return rs
