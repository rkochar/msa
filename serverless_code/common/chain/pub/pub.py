def pub(headers, query_string_parameters):
    head = headers.get("header") or "noheader"
    query = query_string_parameters.get("query") or "noquery"
    d = {"header": head, "query": query}
    return str(d)
