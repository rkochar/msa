from os import makedirs
import re

from pulumi_azure.appservice import FunctionApp
from pulumi import export, Output, ResourceOptions
from pulumi_command.local import Command

from utils.helpers import bash_command
from utils.synthesizer import replace


def create_function_app(code_path, name, handler, environment, http_trigger=True, sqs=None, ram=256, runtime="python3.10", msazure_config=None, opts=None):
    language = re.split('\d+', runtime)[0]
    version = runtime.split(language)[1]
    function_app = FunctionApp(name,
                               name=name,
                               resource_group_name=msazure_config.get("resource_group").name,
                               storage_account_name=msazure_config.get("storage_account").name,
                               storage_account_access_key=msazure_config.get("storage_account").primary_access_key,
                               app_service_plan_id=msazure_config.get("app_service_plan").id,

                               location=msazure_config.get("resource_group").location,
                               os_type="linux",
                               version="~4",

                               https_only=False,

                               app_settings={
                                   "WEBSITE_RUN_FROM_PACKAGE": "",
                                   "FUNCTIONS_WORKER_RUNTIME": language,
                                   # "APPINSIGHTS_INSTRUMENTATIONKEY": ""
                               },

                               site_config={
                                   "linux_fx_version": f"{language}|{version}",
                                   "use_32_bit_worker_process": False,
                               },
                               opts=opts
                               )
    function_code = f"./serverless_code/output/msazure/{code_path}"
    create_function_template(function_code, code_path, name)
    deploy_function(function_code, name, msazure_config, opts=ResourceOptions(depends_on=[function_app]))
    #deploy_function_code(function_code, name, handler, opts=ResourceOptions(depends_on=[function_app]))
    export(f"lambda-{name}-hostname", function_app.default_hostname)
    return function_app


def create_function_template(function_code, code_path, name):
    makedirs(function_code, exist_ok=True)
    command = bash_command(f"create-function-template-{name}",
                           command="func init --python --model V2",
                           path=function_code,
                           debug=True
)
    synthesize_command = bash_command(f"synthesize-function-template-{name}",
                                      command=f"yes | cp -i tmp_files/{code_path}/function_app.py {code_path}/ && cp ./../../templates/msazure/replace.sh {code_path}/",
                                      path="./serverless_code/output/msazure",
                                      debug=True,
                                      opts=ResourceOptions(depends_on=[command])
                                      )
    return command


def deploy_function(function_code, name, msazure_config, opts=None):
    get_url = "URL=$(az storage account show-connection-string --name storageaccountfaasmonad --resource-group resourcegroup | jq '.connectionString')"
    command = bash_command(f"{name}-insert-storage-account-url",
                           command="sh replace.sh",
                           #command="sed -i 's|azurewebjobsstorage|$(az storage account show-connection-string --name storageaccountfaasmonad --resource-group resourcegroup | jq \'.connectionString\')|g' local.settings.json",
                           path=function_code,
                           #debug=True,
                           opts=opts
                           )
    #storage_account_connection_url = msazure_config.get("storage_account_connection_url") or "Not Found"
    #replace(f"{function_code}/local.settings.json", '"AzureWebJobsStorage": ""', f'"AzureWebJobsStorage": {storage_account_connection_url}')
    #print(f"storage_account_connection_url: {_account_connection_url}")


def deploy_function_code(function_code, name, handler, opts=None):
    deploy_code_command = Command(f"deploy-function-code-to-{name}",
                                  interpreter=["/bin/sh", "-c"],
                                  dir=function_code,
                                  create=f"sleep 15 && func azure functionapp publish {name}",
                                  opts=opts
                                  )

    endpoint = deploy_code_command.stdout.apply(
        lambda output: [line.split("Invoke url: ")[1] for line in output.split("\n") if "Invoke url:" in line][0]
    )

    export(f"function-app-{name}-endpoint", endpoint)
