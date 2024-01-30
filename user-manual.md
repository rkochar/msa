# User Manual
This is light weight documentation intended for survey participants. This document guides developers in writing code (cloud agnostic business logic and infrastructure code) while README.md contains information for deploying the code to a cloud provider.

Serverless functions have unique code for every cloud provider which makes being agnostic challenging. To solve this, templates are offered which will use the monadic approach to unify the unique specifications and requirements of every cloud provider. The beauty of monads is that the heavy lifting is done behind the scenes and developers are not exposed to any of the nastiness. A similar approach is taken with cloud agnostic infrastructure code.

## Building a Simple API Application
Create an API with two endpoints, `\one` to implement FizzBuzz and `\two` to accept a transaction, validate it, if validation succeeds, send it over a message queue to another serverless function to write it to a database.

### FizzBuzz
It is a classic problem given to beginners to learn if-else statements. A number is given as input and the program will return `Fizz` and `Buzz` if the number if divisible by 3 and 5 respectively. `FizzBuzz` is returned when the number is divisble by both 3 and 5, other return `No FizzBuzz`.

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

### Setup

```python
from utils.monad import Monad

m = Monad()
```

### Serverless Function
Example
```python
lambda_foo = m.create_lambda('foobar-foo', "foobar/foo", "foo.foo", template="http", role=apigw_lambda_iam_role, is_time=False)
```

### Message Queue
Example
```python
sqs_transaction, environment = m.create_message_queue(topic_name='transaction', environment=environment)
```

### SQL Database
Example
```python
sqldb, sqldb_lambda_environment = m.create_sql_database("sqldb", "mysql", "8.0.34", 10, "foouser", "foopass123", "small")
```

### API Gateway
Example
```python
routes = [("/foo", "GET", lambda_foo, "foobar-foo", "lambda for foo"),]
m.create_apigw('foobar', routes, opts=ResourceOptions(depends_on=[lambda_foo], replace_on_changes=["*"], delete_before_replace=True))
```

### IAM Roles
```python
# Basic Lambda Role
apigw_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-basic-role", "lambda-role-attachment", "lambda-iam-policy", "lambda-basic-policy")

# Message Queue
mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-basic-role", "lambda-role-attachment", "sqs-policy", "message-queue-policy"

# SQL
sql_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-basic-role", "sql-attachment", "sql-policy", "mq-sql-policy")
```

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
