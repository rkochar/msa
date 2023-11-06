from utils.monad import Monad
from pulumi import ResourceOptions


def create_mvccdb():
    m = Monad()

    #m.create_sql_database("foobar", "postgres", "12", 10, "foouser", "foopass123", "small")
    sqs_transaction = m.create_message_queue('transaction')
    lambda_role = m.create_role_policy_attachment("lambda-role-attachment", "sns-policy", "policy/aws/lambda-snssqs.json", "apigw-lambda-iam-role", "policy/aws/lambda-apigw.json")

    environment = {"SQS_URL": sqs_transaction.url}
    apigw_lambda_consumer = m.create_lambda('lambda-apigw-consumer', "consumer.consumer", lambda_role, environment, http_trigger=False, topic=sqs_transaction.topic, opts=ResourceOptions(depends_on=[sqs]))

    apigw_lambda_database = m.create_lambda('lambda-apigw-database', "consumer.consumer", lambda_role, environment, opts=ResourceOptions(depends_on=[sql]))

    routes = [
        ("/transaction", "GET", apigw_lambda_consumer, "lambda-apigw-consumer", "lambda for consumer of transactions"),
        # ("/database", "POST", apigw_lambda_database),
    ]
    m.create_apigw('apigw', routes)
