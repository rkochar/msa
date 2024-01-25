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



def bash_command(name, command, path=".", debug=False, opts=None):
    command = Command(f"command-{name}",
                      interpreter=["/bin/sh", "-c"],
                      dir=path,
                      create=command,
                      opts=opts
                      )
    if debug:
        export(f"command-output-{name}", command.stdout)
        export(f"command-output-err-{name}", command.stderr)
    return command


def delete_last_n_lines(file, N):
    with open(file) as f1:
        lines = f1.readlines()

    with open(file, 'w') as f2:
        f2.writelines(lines[:-N])
    f1.close()
    f2.close()


def flatten(d):
    for i in d:
        yield from [i] if not isinstance(i, tuple) else flatten(i)
