import functions_framework


@functions_framework.http
def template(request):
    query_string_parameters = request.args
    headers = request.headers

    body = ""

    return body
