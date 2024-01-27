# User Manual
This is light weight documentation intended for survey participants. This document guides developers in writing code (cloud agnostic business logic and infrastructure code) while README.md contains information for deploying the code to a cloud provider.

Serverless functions have unique code for every cloud provider which makes being agnostic challenging. To solve this, templates are offered which will use the monadic approach to unify the unique specifications and requirements of every cloud provider. The beauty of monads is that the heavy lifting is done behind the scenes and developers are not exposed to any of the nastiness. A similar approach is taken with cloud agnostic infrastructure code.

## Cloud Agnostic Business Logic
### HTTP
A simple HTTP triggered serverless function. Developers can access headers and query parameters passed with the curl request to trigger a the HTTP serverless function.

```python
def <function-name>(headers, query_parameters):
    # Business logic
    return <string>  # This will be the response to your HTTP request
```

### MQ (Message Queue)
Trigger a serverless function by publishing an event to a queue. Infrastructure code is used to setup the trigger (see TODO). The message placed into the queue is made available as a string ready to be used. Note: there is no return, to trigger further computations the serverless function should perform an event such as publishing a message to another queue (see TODO).
```python
def <function-name>(message):
    # Business logic
```

### Pub (Message Queue)
Publish a message to a queue. The connection information for the queue should be passed as an environment variable in infrastructure code.

```python
def <function-name>(<parameters depending on trigger selected>):
    # Business logic
    return <string>  # If you want to send a dict, use str() and parse back to dict in the receiving function
```
### SQL
To interact with a SQL database, this template will handle all connection for developers. `execute_sql_query()` takes a list as input which contains the query as a string to be run against the database. The list allows batching and results are returned as a list.

```python
def <function-name>(<parameters depending on trigger selected>):
    # Business logic
    queries = [query1, query2, ...]
    execute_sql_query(queries)
```

In AWS, RDS lives inside a VPC (Virutal Private Cloud) which means a default Lambda can not access it. A Lambda placed inside the VPC does not have access to public internet wihtout a NAT box or similar expensive tools. The cheapest and reasonably tight is a VPCE (VPC Endpoint) which is opened in the VPC. If a Lambda is triggered by MQ, then the Lambda is placed inside the VPC (no access to public internet) and the VPCE carefully allows a message queue to deliver the message to the Lambda.
<!--- which is opened for Message Queue so HTTP requests of all kinds are not allowed. This means a specific serverless function alone can communicate with the database and this is good for security because that specific serverless function alone has access to the database. -->

## Cloud Agnostic Infrastructure Code
This is achieved through custom base modules. 

`pydoc3 -p 8081` in root dir to generate documentation from docstrings.

<!--
### Lambda
Input: (str: name of lambda, str: <filename>.<function name>, Either[str, IAMRole]role, dict: environment, bool: http_trigger, str: topic, int: min_instance, int: max_instance, int: ram, int: timeout_seconds)
AWS layers require wheels. GCP has a requirements.txt (per lambda).
GCP easily provides min and max lambda instances. AWS has [Provisioned Concurrency](https://aws.amazon.com/blogs/aws/new-provisioned-concurrency-for-lambda-functions/), it is paid. Using the default auto-scaler gives sufficient performace.

### IAM Role
Input: (str: name of role, str: description)
Can not use a ResourceOption because Google treats IAM roles differently than AWS.

### API Gateway
Input: (str: name of apigw, List[Route]: routes)

#### Route
List of tuples.
- **AWS:** (path, http request type, the lambda variable)
- **GCP:** (path, http request type, NA, name of lambda, description)

### Message Queue
Input: (str: topic_name)

### SQL Database
Input: (str: name, str: engine, str: engine_version, int: storage, str: username, str: password, str: server class)
GCP does not use amount of storage (default 10, of server class small). engine is "mysql" or "postgres". Enter version as "major.minor.patch".
AWS will export an endpoint. GCP will export public, private ip addresses and an endpoint. -->
