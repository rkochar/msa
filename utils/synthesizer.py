from shutil import copyfile, copytree, move, rmtree
from os import path

from pulumi import Config

from utils.helpers import replace

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(handler, is_http, environment):
    name, function = handler.split(".")
    if is_http:
        if cloud_provider == "aws":
            synthesize_aws_http(name, function, template="http")
        elif cloud_provider == "gcp":
            synthesize_gcp_http(name, function, template="http")
        elif cloud_provider == "azure":
            synthesize_azure_http(name, function, template="http")
    else:
        if cloud_provider == "aws":
            synthesize_aws_mq(name, function, template="mq", environment=environment)
        elif cloud_provider == "gcp":
            synthesize_gcp_mq(name, function, template="mq")
        elif cloud_provider == "azure":
            synthesize_azure_mq()


def append_user_function(name, function, template, function_parameters):
    new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
    old_file_path = f"./code/common/{name}.py"
    copyfile(f"./templates/{cloud_provider}/{template}.py", new_file_path)

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


def synthesize_gcp_http(name, function, template):
    return synthesize_http(name, function, template, event="request")


def synthesize_azure_http(name, function, template):
    destination = f"./code/output/azure/{name}-{function}"
    if path.exists(destination):
        rmtree(destination)
    copytree(f"./templates/azure/{template}", destination)

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
    replace(new_file_path, "queue_url = os.environ['SQS_']", f"queue_url = os.environ['{queue_name}']")


def synthesize_gcp_mq(name, function, template):
    function_call = "message"
    append_user_function(name, function, template, function_call)


def synthesize_azure_mq(name, function, template):
    pass
