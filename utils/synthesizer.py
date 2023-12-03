from shutil import copyfile, copytree, move, rmtree
from os import path, makedirs

from pulumi import Config

from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

config = Config()
cloud_provider = config.get("cloud_provider")


def synthesize(code_path, handler, template, imports=False):
    name, function = handler.split(".")

    stub = "http" if template.startswith("http") else "mq"
    new_file_path = f"./code/output/{cloud_provider}/{code_path}/{name}.py"
    makedirs(path.dirname(new_file_path), exist_ok=True)
    copyfile(f"./code/templates/{cloud_provider}/{stub}.py", new_file_path)
    if imports:
        copyfile(f"./code/common/{code_path}/requirements.txt", f"./code/output/{cloud_provider}/{code_path}/requirements.txt")
    function_parameters = "headers, query_parameters" if template.startswith("http") else "message"
    new_string = f"body = {function}({function_parameters})"

    if "sql" in template:
        append_file(new_file_path, f"./code/templates/{cloud_provider}/sql.py")
    if template.endswith("_pub"):
        append_file(new_file_path, f"./code/templates/{cloud_provider}/pub.py")
        new_string = f"body = publish_message({function}({function_parameters}))"

    replace(new_file_path, 'body = ""', new_string)
    append_file(new_file_path, f"./code/common/{code_path}/{name}.py")


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


# def make_bucket_object(new_file_path, imports, aws_config, gcp_config):
#     if cloud_provider == "aws":
#         bucket = aws_config[0]
#         import_layer = create_layers(imports, aws_config)
#         zip_file = zip(new_file_path)
#         create_bucket_object(bucket, name, zip_file)
#         return bucket_object, import_layer
#     # elif cloud_provider == "gcp":
#     #     from gcp.storage import create_bucket
#     #     bucket = create_bucket(f"{cloud_provider}-code-bucket")
#     #     bucket_object = bucket.new_object(f"{new_file_path.split('/')[-1]}")
#     #     bucket_object.upload_file(new_file_path)
#     #     return bucket_object
#     else:
#         raise Exception("Invalid cloud provider")
