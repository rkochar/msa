# faas-monad

## Examples
- **foobar:**
- **mvcc:**

## Components

### Lambda
Input: (name of lambda, <filename>.<function name>, role, environment, min_instance, max_instance, ram, timeout_seconds)

### IAM Role
Input: (name of role, description)

### API Gateway
Input: (name of apigw, routes)

#### Routes
List of tuples.
- **AWS:** (<path>, <http request type>, <the lambda variable>)
- **GCP:** (<path>, <http request type>, NA, <name of lambda>, <description>)

### Message Queue

### SQL Database
