from shutil import copyfile, copytree, move, rmtree, move, copymode
from os import path, makedirs, fdopen, remove
from distutils.dir_util import copy_tree
from tempfile import mkstemp

from pulumi import Config

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(code_path, handler, template, imports=[]):
    name, function = handler.split(".")
    stub = "http" if template.startswith("http") else "mq"
    new_file_path = get_new_file_path(code_path, stub, name)

    makedirs(path.dirname(new_file_path), exist_ok=True)
    copyfile(f"./serverless_code/templates/{cloud_provider}/{stub}.py", new_file_path)

    imports, new_string = synthesize_code(new_file_path, function, template, imports)
    replace(new_file_path, 'body = ""', new_string)
    append_file(new_file_path, f"./serverless_code/common/{code_path}/{name}.py")
    replace(new_file_path, "<route>", function)

    synthesize_requirements(code_path, imports)


def synthesize_code(new_file_path, function, template, imports):
    function_parameters = "headers, query_parameters" if template.startswith("http") else "message"
    new_string = f"body = {function}({function_parameters})"

    if "sql" in template:
        append_file(new_file_path, f"./serverless_code/templates/{cloud_provider}/sql.py")
        if cloud_provider == "gcp":
            imports.append("SQLAlchemy")
            imports.append("cloud-sql-python-connector")

    if template.endswith("_pub"):
        append_file(new_file_path, f"./serverless_code/templates/{cloud_provider}/pub.py")
        new_string = f"body = {function}({function_parameters})" + "\n    "
        new_string += "if not body.startswith('Errors found: '):"+ "\n        " + "body = publish_message(body)"
        if cloud_provider == "gcp":
            imports.append("google-cloud-pubsub")

    return imports, new_string


def synthesize_requirements(code_path, imports=[]):
    req_file_path = f'./serverless_code/output/{cloud_provider}/{code_path}/requirements.txt'

    if len(imports) > 0:
        makedirs(path.dirname(req_file_path), exist_ok=True)
        with open(req_file_path, mode='a', encoding='utf-8') as reqfile:
            reqfile.writelines(list(map(lambda x: x + "\n", imports)))


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
        copy_tree(f"./serverless_code/templates/{cloud_provider}/{stub}", f"./serverless_code/output/{cloud_provider}/{code_path}")
        return f"./serverless_code/output/{cloud_provider}/{code_path}/function_app.py"
    else:
        return f"./serverless_code/output/{cloud_provider}/{code_path}/{name}.py"

