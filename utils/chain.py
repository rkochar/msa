from pulumi import ResourceOptions

from utils.monad import Monad


def chain():
    m = Monad()

    mq, mq_environment = m.create_message_queue(topic_name='transaction')
    dynamodb, dynamodb_environment = m.create_dynamodb("transaction", attributes=[("header", "S"), ("query", "S")], hash_key="header", range_key="query", stream_enabled=True, stream_view_type="NEW_AND_OLD_IMAGES")

    mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-basic-role", "lambda-role-attachment", "mq-iam-policy", "message-queue-policy")
    publish_lambda = m.create_lambda('publish', "chain/pub", "pub.pub", template="http_pub", environment=mq_environment, role=mq_lambda_iam_role, is_timed=True, is_telemetry=True, opts=ResourceOptions(depends_on=[mq], delete_before_replace=True, replace_on_changes=["*"]))
    subscribe_lambda = m.create_lambda('subscribe', "chain/sub", "sub.sub", template="mq_dynamodb", role=mq_lambda_iam_role, mq_topic=mq, environment=mq_environment | dynamodb_environment, is_timed=True, is_telemetry=True, opts=ResourceOptions(depends_on=[mq, dynamodb], delete_before_replace=True, replace_on_changes=["*"]))

    dynamodb_lambda_iam_role = m.create_iam("dynamodb-lambda-iam-role", "lambda-basic-role", "lambda-dynamodb-role-attachment", "dynamodb-iam-policy", "dynamodb-policy")
    dynamodb_lambda = m.create_lambda("dynamodb", "chain/dyn", "dyn.dyn", template="dynamodb", dynamodb=dynamodb, environment=dynamodb_environment, role=dynamodb_lambda_iam_role)

    routes = [
        ("/publish", "GET", publish_lambda, "publish", "lambda that will publish param query and header head to a mq topic"),
    ]
    m.create_apigw('chain', routes, opts=ResourceOptions(depends_on=[publish_lambda, subscribe_lambda], replace_on_changes=["*"], delete_before_replace=True))
