from utils.monad import Monad
from pulumi import ResourceOptions


def create_mq():
    m = Monad()
    environment = {}

    sqs_transaction, environment = m.create_message_queue(topic_name='transaction', environment=environment)

    # sqldb = m.create_sql_database("foobar", "mysql", "8.0.34", 10,
    #                               "foouser", "foopass123", "small")

    mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-role",
                                      "lambda-role-attachment", "sns-policy", "mq-role")

    lambda_mq_foo = m.create_lambda('lambda-mq', "mq.print_message", role=mq_lambda_iam_role, environment=environment,
                                    http_trigger=False, mq_topic=sqs_transaction,
                                    opts=ResourceOptions(depends_on=[sqs_transaction]))  #, sqldb
