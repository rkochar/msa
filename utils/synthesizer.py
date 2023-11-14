from shutil import copyfile

from pulumi import Config

from utils.helpers import replace

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(handler, is_http):
    name, function = handler.split(".")
    if is_http:
        if cloud_provider == "aws":
            synthesize_aws_http(name, function)
        elif cloud_provider == "gcp":
            synthesize_gcp_http(name, function)
        elif cloud_provider == "azure":
            synthesize_azure_http()


def synthesize_aws_http(name, function):
    return synthesize_http(name, function, event="event")


def synthesize_gcp_http(name, function):
    return synthesize_http(name, function, event="request")


def synthesize_http(name, function, event):
    new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
    old_file_path = f"./code/common/{name}.py"
    copyfile(f"./templates/{cloud_provider}/http.py", new_file_path)

    replace(new_file_path, 'body = ""', f"body = {function}({event}, headers, query_string_parameters)")

    new_file = open(new_file_path, "a+")
    old_file = open(old_file_path, "r")
    new_file.write("\n\n")
    new_file.write(old_file.read())

    new_file.close()
    old_file.close()


def synthesize_azure_http():
    pass
