from shutil import copyfile, copytree, move, rmtree, move, copymode
from os import path, makedirs, fdopen, remove
from distutils.dir_util import copy_tree
from tempfile import mkstemp

from pulumi import Config

config = Config()
cloud_provider = config.get("cloud_provider")
NEW_LINE_TAB, TAB = "\n    ", "    "


def synthesize(function_name, code_path, handler, template, imports=[], is_time=False, is_telemetry=False):
    name, function = handler.split(".")
    stub = get_stub(template)
    new_file_path = get_new_file_path(code_path, stub, name)

    makedirs(path.dirname(new_file_path), exist_ok=True)
    copyfile(f"./serverless_code/templates/{cloud_provider}/{stub}.py", new_file_path)

    replace(new_file_path, 'name = ""', f'name = "{function_name}"')
    imports, new_string = synthesize_code(new_file_path, function, stub, template, imports)
    setup_template(new_file_path, new_string, code_path, name, function, function_name)
    telemetry_monad(is_time, is_telemetry, new_file_path, template)
    time_monad(is_time, is_telemetry, new_file_path)

    synthesize_requirements(code_path, imports)
    synthesize_helpers(code_path)


def time_monad(is_time, is_telemetry, new_file_path):
    START_TIME, START_TIME_STRING, END_TIME = "<start-time>", "start_time = time()", "<end-time>"
    if is_time:
        replace(new_file_path, START_TIME, START_TIME_STRING)
        replace(new_file_path, '"body": body,', '"body": body, "execution_time": str(time() - start_time), ')

        end_time_string = 'end_time = time()' + NEW_LINE_TAB + 'execution_time = str(end_time - start_time)' + NEW_LINE_TAB + 'print(f"execution_time: {execution_time}")'
        replace(new_file_path, END_TIME, end_time_string)
    else:
        if is_telemetry:
            replace(new_file_path, START_TIME, START_TIME_STRING)
        replace(new_file_path, TAB + START_TIME + "\n", "")
        replace(new_file_path, TAB + END_TIME + "\n", "")


def telemetry_monad(is_time, is_telemetry, new_file_path, template):
    if is_telemetry:
        start_span_string = "hex = uuid4().hex"
        start_span_string += NEW_LINE_TAB + 'span = {"span_id": hex, "name": name, "start_time": start_time, "annotations": []}' + NEW_LINE_TAB + 'span["span_depth"], span["parent_span_id"] = 1, None'
        replace(new_file_path, "<start-span>", start_span_string)

        span_string = 'span["end_time"] = ' + ("end_time" if is_time else "time()") + NEW_LINE_TAB + (
            "" if template.startswith(
                "http") else TAB) + 'span["execution_time"] = str(span.get("end_time") - span.get("start_time"))'
        replace(new_file_path, "<end-span>", span_string)
        replace(new_file_path, '"body": body,', f'"body": body, "span": span, ')

        configure_span(new_file_path, template)
    else:
        replace(new_file_path, TAB + TAB + "<end-span>\n", "")
        replace(new_file_path, TAB + "<end-span>\n", "")
        replace(new_file_path, "<start-span>", "span, parent_span = None, None")  # TODO: test


def configure_span(new_file_path, template):
    if template == "mq" or "_mq" in template:
        pass
    else:
        replace(new_file_path, "<span_depth>", "1")
        replace(new_file_path, "<parent_span>", "None")
    # can_not_start_span = ["http", "mq|dynamodb", "dynamodb", "s3"]
    # for t in can_not_start_span:
    #     if template.startswith(t):
    #         replace(new_file_path, "<span_depth>", "1")
    #         replace(new_file_path, "<parent_span>", "None")
    #         return
    #     elif template == "mq" or "_mq" in template:
    #         pass


def setup_template(new_file_path, new_string, code_path, name, function, function_name):
    replace(new_file_path, 'body = ""', new_string)
    append_file(new_file_path, f"./serverless_code/common/{code_path}/{name}.py")
    replace(new_file_path, "<route>", function)  # For azure


def synthesize_code(new_file_path, function, stub, template, imports):
    function_parameters = get_parameters(stub)
    new_string = f"body = {function}({function_parameters})"

    if "_sql" in template:
        append_file(new_file_path, f"./serverless_code/templates/{cloud_provider}/sql.py")
        if cloud_provider == "gcp":
            imports.append("SQLAlchemy")
            imports.append("cloud-sql-python-connector")

    if "_s3" in template:
        append_file(new_file_path, f"./serverless_code/templates/{cloud_provider}/s3_methods.py")
        if cloud_provider == "gcp":
            imports.append("google-cloud-storage")

    if "_dynamodb" in template:
        if cloud_provider == "aws":
            append_file(new_file_path, f"./serverless_code/templates/{cloud_provider}/dynamodb_methods.py")

    if template.endswith("_pub"):
        append_file(new_file_path, f"./serverless_code/templates/{cloud_provider}/pub.py")
        new_string = f"body = {function}({function_parameters})" + NEW_LINE_TAB
        new_string += "if isinstance(body, str) and not body.startswith('Errors found: '):" + NEW_LINE_TAB + TAB + 'body = publish_message(str({"span": span, "body": body}))'
        if cloud_provider == "gcp":
            imports.append("google-cloud-pubsub")

    if "mq|dynamodb" in template:
        if cloud_provider == "aws":
            new_string = f"body = {function}(event, context)"
    return imports, new_string


def synthesize_requirements(code_path, imports=[]):
    req_file_path = f'./serverless_code/output/{cloud_provider}/{code_path}/requirements.txt'

    if len(imports) > 0:
        makedirs(path.dirname(req_file_path), exist_ok=True)
        with open(req_file_path, mode='a', encoding='utf-8') as reqfile:
            reqfile.writelines(list(map(lambda x: x + "\n", imports)))


def synthesize_helpers(code_path):
    if path.exists(f"./serverless_code/common/{code_path}/helpers"):
        copy_tree(f"./serverless_code/common/{code_path}/helpers",
                  f"./serverless_code/output/{cloud_provider}/{code_path}/helpers")


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


def append_file(new_file_path, old_file_path):
    new_file = open(new_file_path, "a+")
    old_file = open(old_file_path, "r")
    new_file.write("\n\n")
    new_file.write(old_file.read())

    new_file.close()
    old_file.close()


def get_new_file_path(code_path, stub, name):
    if cloud_provider == "msazure":
        copy_tree(f"./serverless_code/templates/{cloud_provider}/{stub}",
                  f"./serverless_code/output/{cloud_provider}/{code_path}")
        return f"./serverless_code/output/{cloud_provider}/{code_path}/function_app.py"
    else:
        return f"./serverless_code/output/{cloud_provider}/{code_path}/{name}.py"


def get_stub(template):
    if template.startswith("http"):
        return "http"
    elif template.startswith("mq_") or template == "mq":
        return "mq"
    elif template.startswith("dynamodb_") or template == "dynamodb":
        return "dynamodb"
    elif template.startswith("s3"):
        return "s3"
    else:
        return "mq|dynamodb"


def get_parameters(stub):
    match stub:
        case "http":
            return "headers, query_parameters"
        case "mq":
            return 'message["body"]'
        case "dynamodb":
            return "event.get('Records')"
        case "s3":
            if cloud_provider == "aws":
                return "event['Records'][0]['s3']"
            elif cloud_provider == "gcp":
                return 'message'
