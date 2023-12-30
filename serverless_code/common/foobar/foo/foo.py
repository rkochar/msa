def foo(headers, query_parameters):
    name = query_parameters.get("name") or "FaaS"
    return f"Hello {name}"
