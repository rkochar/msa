from pulumi import ResourceOptions, Input, Output, export
from pulumi_command.local import Command
# from pulumi_azure_native import storage, resources

from fileinput import input
import sys


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


def delete_last_n_lines(file, N):
    with open(file) as f1:
        lines = f1.readlines()

    with open(file, 'w') as f2:
        f2.writelines(lines[:-N])
    f1.close()
    f2.close()
