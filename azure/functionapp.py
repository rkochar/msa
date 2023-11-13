import re

from pulumi_azure.appservice import FunctionApp
from pulumi_azure import storage
from pulumi import export, Output


def create_function_app(name, environment, http_trigger=True, sqs=None, ram=256, runtime="python3.10",
                        azure_config=None, opts=None):
    language = re.split('\d+', runtime)[0]
    version = runtime.split(language)[1]
    resource_group, storage_account, storage_container, app_service_plan = azure_config
    function_app = FunctionApp(name,
                               resource_group_name=resource_group.name,
                               storage_account_name=storage_account.name,
                               storage_account_access_key=storage_account.primary_access_key,
                               app_service_plan_id=app_service_plan.id,

                               location=resource_group.location,
                               os_type="linux",
                               version="~4",

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

    export(f"lambda-{name}-hostname", function_app.default_hostname)
    return function_app


def signature(resource_group, account, app_container):
    pass
    # https://www.pulumi.com/registry/packages/azure/api-docs/storage/getaccountblobcontainersas/
    # https://www.pulumi.com/registry/packages/azure/api-docs/apimanagement/api/