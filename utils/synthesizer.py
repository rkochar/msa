from shutil import copyfile, copytree, move, rmtree
from os import path

from pulumi import Config

from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(handler, template, environment):
    name, function = handler.split(".")

    stub = "http" if template.startswith("http") else "mq"
    new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
    copyfile(f"./code/templates/{cloud_provider}/{stub}.py", new_file_path)
    function_parameters = "headers, query_parameters" if template.startswith("http") else "message"
    new_string = f"body = {function}({function_parameters})"

    if "sql" in template:
        append_file(new_file_path, f"./code/templates/{cloud_provider}/sql.py")
    if template.endswith("_pub"):  # TODO: AWS needs the MQ name.
        append_file(new_file_path, f"./code/templates/{cloud_provider}/pub.py")
        new_string = f"body = publish_message({function}({function_parameters}))"

    replace(new_file_path, 'body = ""', new_string)
    append_file(new_file_path, f"./code/common/{name}.py")

    # match cloud_provider:
    #     case "aws":
    #         copy_aws_template(name, function, template)
    #     case "gcp":
    #         copy_gcp_template(name, function, template)
    #     case "azure":
    #         pass


# def copy_gcp_template(name, function, template):
#     stub = "http" if template.startswith("http") else "mq"
#     new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
#     copyfile(f"./code/templates/{cloud_provider}/{stub}.py", new_file_path)
#     function_parameters = "headers, query_parameters" if template.startswith("http") else "message"
#     new_string = f"body = {function}({function_parameters})"
#
#     if "sql" in template:
#         append_file(new_file_path, f"./code/templates/{cloud_provider}/sql.py")
#     if template.endswith("_pub"):
#         append_file(new_file_path, f"./code/templates/{cloud_provider}/pub.py")
#         new_string = f"body = publish_message({function}({function_parameters}))"
#
#     replace(new_file_path, 'body = ""', new_string)
#     append_file(new_file_path, f"./code/common/{name}.py")


# def copy_aws_template(name, function, template):
#     stub = "http" if template.startswith("http") else "mq"
#     new_file_path = f"./code/output/{cloud_provider}/{name}-{function}.py"
#     copyfile(f"./code/templates/{cloud_provider}/{stub}.py", new_file_path)
#     function_parameters = "headers, query_parameters" if template.startswith("http") else "message"
#     new_string = f"body = {function}({function_parameters})"
#
#     if "sql" in template:
#         append_file(new_file_path, f"./code/templates/{cloud_provider}/sql.py")
#     if template.endswith("_pub"):
#         append_file(new_file_path, f"./code/templates/{cloud_provider}/pub.py")
#         new_string = f"body = publish_message({function}({function_parameters}))"
#
#     replace(new_file_path, 'body = ""', new_string)
#     append_file(new_file_path, f"./code/common/{name}.py")

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
