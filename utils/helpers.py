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
                                  #create="az ad signed-in-user show --query userPrincipalName --output tsv",
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

# def get_connection_string(resource_group, account):
#    # Retrieve the primary storage account key.
#    storage_account_keys = Output.all(resource_group.name, account.name).apply(lambda args:  storage.list_storage_account_keys(resource_group_name=args[0],account_name=args[1]))
#
#    primary_storage_key = storage_account_keys.apply(lambda accountKeys: accountKeys.keys[0].value)
#
#    # Build the connection string to the storage account.
#    return Output.concat("DefaultEndpointsProtocol=https;AccountName=",
#                         account.name,
#                         ";AccountKey=",
#                         primary_storage_key
#                         )
#
#
# def signed_blob_read_url(blob_name, container_name, account_name, resource_group_name):
#    blob_sas = storage.list_storage_account_service_sas(account_name=account_name,
#                                                        resource_group_name=resource_group_name,
#                                                        protocols=storage.HttpProtocol.HTTPS,
#                                                        shared_access_expiry_time="2030-01-01",
#                                                        shared_access_start_time="2021-01-01",
#                                                        resource=storage.SignedResource.C,
#                                                        permissions=storage.Permissions.R,
#                                                        canonicalized_resource=f"/blob/{account_name}/{container_name}",
#                                                        content_type="application/json",
#                                                        cache_control="max-age=5",
#                                                        content_disposition="inline",
#                                                        content_encoding="deflate")
#    return Output.concat("https://", account_name,
#                         ".blob.core.windows.net/",
#                         container_name, "/", blob_name, "?", blob_sas.service_sas_token)
