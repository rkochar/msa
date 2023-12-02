import functions_framework
from os import getenv


@functions_framework.http
def template(request):
    query_parameters = request.args
    headers = request.headers

    body = ""

    return body
