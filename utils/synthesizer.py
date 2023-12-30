from shutil import copyfile, copytree, move, rmtree
from os import path, makedirs

from pulumi import Config

from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(code_path, handler, template, imports=[]):
    name, function = handler.split(".")

    stub = "http" if template.startswith("http") else "mq"
    new_file_path, req_file_path = f"./serverless_code/output/{cloud_provider}/{code_path}/{name}.py", f'./serverless_code/output/{cloud_provider}/{code_path}/requirements.txt'
    makedirs(path.dirname(new_file_path), exist_ok=True)
    copyfile(f"./serverless_code/templates/{cloud_provider}/{stub}.py", new_file_path)

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

    replace(new_file_path, 'body = ""', new_string)
    append_file(new_file_path, f"./serverless_code/common/{code_path}/{name}.py")

    if len(imports) > 0:
        makedirs(path.dirname(req_file_path), exist_ok=True)
        with open(req_file_path, mode='wt', encoding='utf-8') as reqfile:
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

