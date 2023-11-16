from subprocess import run, PIPE, STDOUT
from os import getcwd, chdir

from pulumi import ComponentResource, export

import pulumi_azure as azure

# class DeployFunctionCode(ComponentResource):
#
#     def __init__(self, function_app, handler, opts=None):
#         super().__init__("azure:deployfunctioncode:DeployFunctionCode", f"{function_app}-code", None, opts)
#
#         handler_path = handler.replace(".", "-")
#         output = run(["func", "azure", "functionapp", "publish", function_app],
#                      cwd=f"./code/azure/{handler_path}",
#                      stdout=PIPE,
#                      stderr=STDOUT,
#                      )
#         print("Deploying code to function_app")
#         print(output.stdout.decode("utf-8").splitlines())
#             # if line.contains("Invoke url:"):
#             #     export(f"{function_app}-endpoint", line.split("Invoke url: ")[1])
#         # print(f"Deploying code to function_app {function_app}\n{output}")

