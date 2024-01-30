from pulumi import ResourceOptions

from utils.monad import Monad


def chain():
    m = Monad()

    mq, mq_environment = m.create_message_queue(topic_name='transaction')

    mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-basic-role", "lambda-role-attachment", "mq-iam-policy", "message-queue-policy")
    publish_lambda = m.create_lambda("chain/pub", 'publish', "pub.pub", template="http_pub", environment=mq_environment, role=mq_lambda_iam_role, is_timed=True, span=True, opts=ResourceOptions(depends_on=[mq], delete_before_replace=True, replace_on_changes=["*"]))
    subscribe_lambda = m.create_lambda("chain/sub", 'subscribe', "sub.sub", template="mq", role=mq_lambda_iam_role, mq_topic=mq, environment=mq_environment, is_timed=True, span=True, opts=ResourceOptions(depends_on=[mq], delete_before_replace=True, replace_on_changes=["*"]))

    routes = [
        ("/publish", "GET", publish_lambda, "publish", "lambda that will publish param query and header head to a mq topic"),
    ]
    m.create_apigw('chain', routes, opts=ResourceOptions(depends_on=[publish_lambda, subscribe_lambda],
                                                         replace_on_changes=["*"], delete_before_replace=True))
