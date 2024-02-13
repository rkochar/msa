def template(event, context):
    name = ""
    <start-time>
    <start-span>

    body = ""

    <end-time>
    <end-span>

    return {
        "statusCode": 200,
        "body": json.dumps({"body": body,})
    }
