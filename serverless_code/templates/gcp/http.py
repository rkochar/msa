import functions_framework
from os import getenv
from time import time


@functions_framework.http
def template(request):
    query_parameters = request.args
    headers = request.headers
    start_time = time()

    body = ""

    return {"body": body, "execution_time": str(time() - start_time)}, 200
