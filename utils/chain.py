from pulumi import ResourceOptions

from utils.monad import Monad


def chain():
    m = Monad()

    mq, mq_environment = m.create_message_queue(topic_name='transaction')

    mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-role",
                                      "lambda-role-attachment", "mq-policy", "message-queue-role")
    publish_lambda = m.create_lambda('publish', "chain.pub", template="http_pub", environment=mq_environment,
                                     role=mq_lambda_iam_role, opts=ResourceOptions(depends_on=[mq]))
    subscribe_lambda = m.create_lambda('subscribe', "chain.sub", template="mq", role=mq_lambda_iam_role, mq_topic=mq,
                                       environment=mq_environment, opts=ResourceOptions(depends_on=[mq]))

    routes = [
        ("/publish", "GET", publish_lambda, "publish",
         "lambda that will publish param query and header head to a mq topic"),
    ]
    m.create_apigw('chain', routes, opts=ResourceOptions(depends_on=[publish_lambda, subscribe_lambda],
                                                         replace_on_changes=["*"], delete_before_replace=True))
