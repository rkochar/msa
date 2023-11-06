# faas-monad

## Examples
- **foobar:**
- **mvcc:**

## Components

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
AWS will export an endpoint. GCP will export public, private ip addresses and an endpoint.
