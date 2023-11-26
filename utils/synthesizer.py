from shutil import copyfile, copytree, move, rmtree
from os import path

from pulumi import Config

from utils.helpers import replace, delete_last_n_lines

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(handler, template, environment):
    name, function = handler.split(".")
    stub = template
    if "pub" in template:
        stub = template[:template.rfind("_")]
    match cloud_provider:
        case "aws":
            copy_aws_template(name, function, template, stub)
        case "gcp":
            copy_gcp_template(name, function, template, stub)
        case "azure":
            pass


def copy_gcp_template(name, function, template, stub):
    # Copy stub
    new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
    copyfile(f"./code/templates/test{cloud_provider}/{stub}.py", new_file_path)

    if template.endswith("_pub"):
        pub = open("./code/templates/testgcp/pub.txt", "r").read()
        replace(new_file_path, 'body = ""', pub)
        delete_last_n_lines(new_file_path, 3)

    if "sql" in template:
        append_file(new_file_path, f"./code/templates/testgcp/sql.py")

    function_parameters = get_gcp_function_parameters(template)
    append_user_function(name, function, new_file_path, function_parameters)

    return new_file_path


def get_gcp_function_parameters(template):
    if template.startswith("http"):
        return "headers, query_parameters"
    elif template.startswith("mq"):
        return "message"


def copy_aws_template(name, function, template, stub):
    new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
    copyfile(f"./code/templates/{cloud_provider}/{stub}.py", new_file_path)


def append_file(new_file_path, old_file_path):
    new_file = open(new_file_path, "a+")
    old_file = open(old_file_path, "r")
    new_file.write("\n\n")
    new_file.write(old_file.read())

    new_file.close()
    old_file.close()


def append_user_function(name, function, new_file_path, function_parameters):
    old_file_path = f"./code/common/{name}.py"

    replace(new_file_path, 'body = ""', f"body = {function}({function_parameters})")

    new_file = open(new_file_path, "a+")
    old_file = open(old_file_path, "r")
    new_file.write("\n\n")
    new_file.write(old_file.read())

    new_file.close()
    old_file.close()

    return new_file_path


def synthesize_aws_http(name, function, template):
    return synthesize_http(name, function, template, event="event")


def synthesize_azure_http(name, function, template):
    destination = f"./code/output/azure/{name}-{function}"
    if path.exists(destination):
        rmtree(destination)
    copytree(f"./code/templates/azure/{template}", destination)

    function_call = "req, headers, query_string_parameters"
    template = f"{template}/function_app"
    new_file_path = append_user_function(name, function, template, function_call)

    replace(new_file_path, "<route>", f"{name}-{function}")
    move(new_file_path, f"{destination}/function_app.py")


def synthesize_http(name, function, template, event):
    function_call = f"{event}, headers, query_string_parameters"
    append_user_function(name, function, template, function_call)


def synthesize_mq(name, function, template):
    function_call = f"message"  # TODO: cleanup
    append_user_function(name, function, template, function_call)


def synthesize_aws_mq(name, function, template, environment):
    function_call = "message"
    new_file_path = append_user_function(name, function, template, function_call)

    queue_name = next(k for k in environment.keys() if k.startswith("SQS_"))
    replace(new_file_path, 'queue_env_name = ""', f"queue_env_name = '{queue_name}'")


def synthesize_azure_mq(name, function, template):
    pass


def synthesize_aws_http_pub(name, function, template, environment):
    function_call = f"headers, query_string_parameters"
    new_file_path = append_user_function(name, function, template, function_call)

    queue_name = next(k for k in environment.keys() if k.startswith("SQS_"))
    replace(new_file_path, 'queue_env_name = ""', f"queue_env_name = '{queue_name}'")
