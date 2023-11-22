def pub(headers, query_string_parameters):
    head = headers.get("head") or "nohead"
    query = query_string_parameters.get("query") or "noquery"
    d = {"head": head, "query": query}
    return str(d)


def sub(message):
    print(f"Message received at sub: {message}")
