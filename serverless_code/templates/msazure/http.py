import azure.functions as func
import datetime
import json
import logging
from time import time

app = func.FunctionApp()

@app.route(route="<route>", auth_level=func.AuthLevel.ANONYMOUS)
def template(req: func.HttpRequest) -> func.HttpResponse:
    start_time = time()
    query_parameters = req.params
    headers = req.headers

    body = ""

    return func.HttpResponse(
        body=json.dumps({"body": body, "execution_time": str(time() - start_time)}),
        mimetype="application/json",
        status_code=200
    )
