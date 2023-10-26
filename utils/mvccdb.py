from utils.distribute import create_apigw, create_lambda, create_iam_role, create_iam_policy, create_role_policy_attachment, create_sns_topic, create_sqs, create_sql_database
from pulumi import ResourceOptions


def create_mvccdb():
    sql = create_sql_database("foobardb", "mysql", "8.0.33", 10, "db.t3.micro", "foobase", "foobar123")
    sqs = create_sqs('transaction')
    lambda_role = create_role_policy_attachment("lambda-role-attachment", "sns-policy", "policy/aws/lambda-snssqs.json",
                                                "apigw-lambda-iam-role", "policy/aws/lambda-apigw.json")
    environment = {"SQS_URL": sqs.url}
    apigw_lambda_consumer = create_lambda('lambda-apigw-consumer', "consumer.consumer", lambda_role, environment, project="/mvccdb", opts=ResourceOptions(depends_on=[sqs]))
    apigw_lambda_database = create_lambda('lambda-apigw-database', "consumer.consumer", lambda_role, environment, project="/mvccdb", opts=ResourceOptions(depends_on=[sql]))

    routes = [
        ("/", "GET", apigw_lambda_consumer),
        # ("/transaction", "POST", apigw_lambda_database),
    ]
    create_apigw('apigw', routes)