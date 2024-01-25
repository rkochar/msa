import functions_framework
from os import getenv
from time import time
from uuid import uuid4


@functions_framework.http
def template(request):
    name = ""
    <start-time>
    <start-span>
    query_parameters, headers = request.args, request.headers

    body = ""

    <end-time>
    <end-span>

    return {"body": body,}, 200
