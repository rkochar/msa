import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()


@app.route(route="bar", auth_level=func.AuthLevel.ANONYMOUS)
def hello_world(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    headers = dict(req.headers)
    amount = headers.get("amount") or -1

    return func.HttpResponse(
        f"This is bar. amount: {amount}",
        status_code=200
    )
