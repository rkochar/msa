from pulumi_azure.storage import Blob

from pulumi import FileArchive, export, Output

from shutil import make_archive


def create_storage_blob(name, functionapp, azure_config=None, opts=None):
    resource_group, storage_account, storage_container, app_service_plan = azure_config
    file = "./serverless_code/azure/" + functionapp
    make_archive(file, "zip", file)
    blob = Blob(
        name,
        storage_account_name=storage_account.name,
        storage_container_name=storage_container.name,
        type="Block",
        source=FileArchive(f"{file}.zip")
    )

    export("sas", Output.concat("https://", storage_account.name, ".blob.core.windows.net/", storage_container.name, "/", blob.name, "?", storage_account.primary_blob_connection_string))
    return blob
