import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.route(route="<route>", auth_level=func.AuthLevel.ANONYMOUS)
def template(req: func.HttpRequest) -> func.HttpResponse:
    query_string_parameters = req.params
    headers = req.headers

    body = ""

    return func.HttpResponse(
        body=body,
        status_code=200
    )

