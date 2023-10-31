from utils.distribute import Distribute
from pulumi import ResourceOptions


def create_mvccdb():
    d = Distribute()
    sql = d.create_sql_database("mvccdb", "mysql", "8.0.33", 10, "db.t3.micro", "foobase", "foobar123")
    sqs = d.create_sqs('transaction')
    lambda_role = d.create_role_policy_attachment("lambda-role-attachment", "sns-policy", "policy/aws/lambda-snssqs.json",
                                                  "apigw-lambda-iam-role", "policy/aws/lambda-apigw.json")
    environment = {"SQS_URL": sqs.url}
    apigw_lambda_consumer = d.create_lambda('lambda-apigw-consumer', "consumer.consumer", lambda_role, environment, opts=ResourceOptions(depends_on=[sqs]))
    apigw_lambda_database = d.create_lambda('lambda-apigw-database', "consumer.consumer", lambda_role, environment, opts=ResourceOptions(depends_on=[sql]))

    routes = [
        ("/transaction", "GET", apigw_lambda_consumer),
        # ("/database", "POST", apigw_lambda_database),
    ]
    d.create_apigw('apigw', routes)