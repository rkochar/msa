import re

from pulumi_azure.appservice import FunctionApp
from pulumi_azure import storage
from pulumi import export, Output, ResourceOptions

from utils.helpers import deploy_function_code


def create_function_app(name, handler, environment, http_trigger=True, sqs=None, ram=256, runtime="python3.10",
                        azure_config=None, opts=None):
    language = re.split('\d+', runtime)[0]
    version = runtime.split(language)[1]
    resource_group, storage_account, storage_container, app_service_plan = azure_config
    function_app = FunctionApp(name,
                               name=name,
                               resource_group_name=resource_group.name,
                               storage_account_name=storage_account.name,
                               storage_account_access_key=storage_account.primary_access_key,
                               app_service_plan_id=app_service_plan.id,

                               location=resource_group.location,
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
                               }
                               )

    deploy_function_code(name, handler, opts=ResourceOptions(depends_on=[function_app]))
    export(f"lambda-{name}-hostname", function_app.default_hostname)
    return function_app

