from os import makedirs
import re

from pulumi_azure.appservice import FunctionApp
from pulumi import export, Output, ResourceOptions, Config
from pulumi_command.local import Command

from utils.helpers import bash_command
from utils.synthesizer import replace


config = Config("azure")
location = config.get("location") or "West Europe"


def create_function_app(code_path, name, handler, environment, http_trigger=True, sqs=None, ram=256, runtime="python3.10", msazure_config=None, opts=None):
    language = re.split('\d+', runtime)[0]
    version = runtime.split(language)[1]
    function_app = FunctionApp(name,
                               name=name,
                               resource_group_name=msazure_config.get("resource_group_name"),
                               storage_account_name=msazure_config.get("storage_account_name"),
                               storage_account_access_key=Config().get_secret("access-key"),
                               app_service_plan_id=msazure_config.get("app_service_plan").id,
                               location=location,
                               os_type="linux",
                               version="~4",

                               https_only=False,

                               app_settings={
                                   "WEBSITE_RUN_FROM_PACKAGE": "",
                                   "FUNCTIONS_WORKER_RUNTIME": language,
                               },

                               site_config={
                                   "linux_fx_version": f"{language}|{version}",
                                   "use_32_bit_worker_process": False,
                               },
                               opts=opts
                               )
    function_code = f"./serverless_code/output/msazure/{code_path}"
    deploy_function_code(function_code, name, handler, opts=ResourceOptions(depends_on=[function_app]))
    export(f"lambda-{name}-hostname", function_app.default_hostname)
    return function_app


def deploy_function_code(function_code, name, handler, opts=None):
    deploy_code_command = Command(f"deploy-function-code-to-{name}",
                                  interpreter=["/bin/sh", "-c"],
                                  dir=function_code,
                                  create=f"sleep 20 && func azure functionapp publish {name} --build remote",
                                  opts=opts
                                  )

    endpoint = deploy_code_command.stdout.apply(
        lambda output: [line.split("Invoke url: ")[1] for line in output.split("\n") if "Invoke url:" in line][0]
    )
    export(f"function-app-{name}-endpoint", endpoint)
