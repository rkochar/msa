from utils.monad import Monad
from pulumi import ResourceOptions


def create_mq():
    m = Monad()
    environment = {}

    sqs_transaction, environment = m.create_message_queue(topic_name='transaction', environment=environment)

    mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-basic-role",
                                      "lambda-role-attachment", "sns-policy", "message-queue-policy")

    lambda_mq_foo = m.create_lambda("mq", 'lambda-mq', "mq.print_message", role=mq_lambda_iam_role, environment=environment,
                                    template="mq", mq_topic=sqs_transaction,
                                    opts=ResourceOptions(depends_on=[sqs_transaction]))

