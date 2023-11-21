from pulumi import ResourceOptions, Input, Output, export
from pulumi_command.local import Command
# from pulumi_azure_native import storage, resources

from fileinput import input
import sys

from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove


def merge_opts(opts1: ResourceOptions, opts2: ResourceOptions):
    if opts1 is None and opts2 is None:
        return None
    elif opts1 is None:
        return opts2
    elif opts2 is None:
        return opts1
    return ResourceOptions.merge(opts1, opts2)


def deploy_function_code(name, handler, opts):
    handler_path = handler.replace(".", "-")
    code_path = f"./code/output/azure/{handler_path}"
    deploy_code_command = Command(f"deploy-function-code-to-{name}",
                                  interpreter=["/bin/sh", "-c"],
                                  dir=code_path,
                                  create=f"sleep 15 && func azure functionapp publish {name}",
                                  # create="az ad signed-in-user show --query userPrincipalName --output tsv",
                                  opts=opts
                                  )

    endpoint = deploy_code_command.stdout.apply(
        lambda output: [line.split("Invoke url: ")[1] for line in output.split("\n") if "Invoke url:" in line][0]
    )

    export(f"function-app-{name}-endpoint", endpoint)


# def replace(filepath, pattern, new_string):
#     for line in input(filepath, inplace=True):
#         if pattern in line:
#             line = line.replace(pattern, new_string)
#         sys.stdout.write(line)


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


def command_template(name, create, path, debug=False, opts=None):
    command = Command(f"command-{name}",
                      interpreter=["/bin/sh", "-c"],
                      dir=path,
                      create=create,
                      opts=opts
                      )
    if debug:
        export(f"command-output-{name}", command.stdout)
    return command
