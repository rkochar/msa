# MSA - Monadic Approach to Serverless Applications
This repository contains code written for my master thesis at Technical University of Delft.

The Infrastructure of Code tool used is [Pulumi](https://www.pulumi.com/). Get started with
```commandline
pip install requirements.txt
```

## Examples
`__main__.py` is the default starting point of Pulumi. `pulumi preview`, `pulumi up` and `pulumi destroy` are the equivalents of `terragrunt plan`, `terragrunt apply` and `terragrunt destroy`. Run these commands in root directory.

To get started, some sample programs are already provided. Simply uncomment them in the main file to run it.
- **foobar:**: A simple API application with two endpoints `/foo` and `/bar` that point to a serverless function with some business logic. foo is a simple hello world program (`/foo?name=<name>`) and bar is more complex. It imports two packages numpy and pydantic to validate a transaction. Pass headers `sender`, `receiver` and `amount`. Note: in AWS, bar will create a custom layer for Lambda with the imports which can be a challenge if host machine architecture does not match architecture of the Lambda. Set architecture in [Pulumi Config](#Pulumi-Config) to fix this.
- **mvcc:** A Multi Version Concurrency Control database for transactions. TODO: add usage instructions
- **Mapreduce:** A serverless mapreduce
- **Zookeeper:** A serverless Zookeeper

## Support
Serverless applications can make a migration of infrastructure code and business logic in the serverless function (data migration is not yet supported) between AWS and GCP. Azure is not supported because they do not have serverless functions. I do not know what Azure Function Applications are but it is not atl all, in any way a serverless function and in Azure documentation, Azure calls it a [serverless solution](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview?pivots=programming-language-csharp) instead of serverless function. Should Azure add serverless services, MSA can be extended to support Azure.

## Pulumi Config
```commandline
pulumi config set cloud:provider <aws or gcp or azure>
pulumi config set architecture <arm64 or x86_64>

pulumi config set aws:region <region>

pulumi config set gcp:region <region>
pulumi config set gcp:project <project name>

pulumi config set azure:location "West Europe"
```
$$

## TODO and Ideas
- [] Confirm requirements.txt works
- [] Document code
- [] Create documentation for users
- [] Create tutorial for users
- [] Integrate into a CI/CD pipeline
- [] Add some tests
- [] Policy as Code
- [] Serverless functions can also run a docker image. Integrate Packer (image-as-code)?
