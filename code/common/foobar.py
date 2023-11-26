def foo(headers, query_parameters):
    name = query_parameters.get("name") or "FaaS"
    return f"Hello {name}"


def bar(headers, query_parameters):
    sender = headers.get("sender") or -1
    receiver = headers.get("receiver") or -1
    amount = headers.get("amount") or -1
    return f"Transfer {amount} from {sender} to {receiver}"
