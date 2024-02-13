from pulumi import ResourceOptions

from utils.monad import Monad
from json import loads


def zookeeper():
    m = Monad()

    config = loads(open("./serverless_code/common/zookeeper/user_config_final.json").read())
    prefix = f"{config.get('service')}_{config.get('stage')}"
    config["S3_DATA_BUCKET"] = f"{config.get('service')}-{config.get('stage')}-data"
    client_import = "git+https://github.com/spcl/faaskeeper-python"

    iam_role_writer = m.create_iam("writer-lambda-iam-role", "lambda-basic-role", "iam-attachment-dyn-sqs", "lambda-iam-policy-dynamodb", "zookeeper/lambda-writer-policy")
    iam_role_distributor = m.create_iam("distributor-lambda-iam-role", "lambda-basic-role", "iam-attachment-dyn-s3-sqs", "lambda-iam-policy-distributor", "zookeeper/lambda-distributor-policy")
    iam_role_watch = m.create_iam("watch-lambda-iam-role", "lambda-basic-role", "iam-attachment-dyn", "lambda-iam-policy-watch", "zookeeper/lambda-watch-policy")

    common_environment = {
        "VERBOSE": config.get("verbose"),
        "DEPLOYMENT_NAME": config.get("deployment_name"),
        "VERBOSE_LOGGING": config.get("verbose"),
        "USER_STORAGE": config.get("user-storage"),
        "SYSTEM_STORAGE": config.get("system-storage"),
        "DISTRIBUTOR_QUEUE": config.get("distributor-queue"),
    }
    channel_environment = {
        "CLIENT_CHANNEL": config.get("client-channel"),
        "BENCHMARKING": config.get("configuration").get("benchmarking") or False,
        "BENCHMARKING_FREQUENCY": config.get("configuration").get("benchmarking_frequency") or 0,
        "QUEUE_PREFIX": f"{prefix}"
}

    writer_queue, writer_environment = m.create_message_queue(f"{prefix}_writer_sqs")
    distributor_queue, distributor_environment = m.create_message_queue(f"{prefix}_distributor_sqs")
    client_queue, client_environment = m.create_message_queue(f"{prefix}_client_sqs", fifo=False)

    dynamo_state, dynamo_state_environment = m.create_dynamodb(f"{prefix}-state", attributes=[("path", "S")], hash_key="path")
    dynamo_data, dynamo_data_environment = m.create_dynamodb(f"{prefix}-data", attributes=[("path", "S")], hash_key="path")
    dynamo_writer, dynamo_writer_environment = m.create_dynamodb(f"{prefix}-writer", attributes=[("key", "S"), ("timestamp", "S")], hash_key="key", range_key="timestamp", stream_enabled=True, stream_view_type="NEW_IMAGE")
    dynamo_distribute, dynamo_distribute_environment = m.create_dynamodb(f"{prefix}-distribute-queue", attributes=[("key", "S"), ("system_counter", "N")], hash_key="key", range_key="system_counter", stream_enabled=True, stream_view_type="NEW_IMAGE")
    dynamo_users, dynamo_users_environment = m.create_dynamodb(f"{prefix}-users", attributes=[("user", "S")], hash_key="user")
    dynamo_watch, dynamo_watch_environment = m.create_dynamodb(f"{prefix}-watch", attributes=[("path", "S")], hash_key="path")

    # TODO: Check templates, triggers (schedule)
    # TODO: creating layers, code_path
    lambda_writer = m.create_lambda(f'{prefix}-writer', "zookeeper/writer", "writer.handler", environment=common_environment | {"S3_DATA_BUCKET": config.get("S3_DATA_BUCKET")} | channel_environment | writer_environment | dynamo_writer_environment, template="mq|dynamodb", mq_topic=writer_queue, dynamodb=dynamo_writer, role=iam_role_writer, imports=[client_import])
    lambda_distributor = m.create_lambda(f'{prefix}-distributor', "zookeeper/distributor", "distributor.handler", environment=common_environment | distributor_environment | dynamo_distribute_environment, template="mq|dynamodb", mq_topic=distributor_queue, dynamodb=dynamo_distribute, role=iam_role_distributor, imports=[client_import])
    lambda_watch = m.create_lambda(f'{prefix}-watch', "zookeeper/watch", "watch.handler", environment=common_environment | channel_environment, template="http", role=iam_role_watch, imports=[client_import])
    lambda_heartbeat = m.create_lambda(f'{prefix}-heartbeat', "zookeeper/heartbeat", "heartbeat.handler", environment=common_environment, template="http", role=iam_role_watch, imports=[client_import])

    # DynamoDB
    # TODO: stream view type
    s3_data = m.create_bucket(config.get("S3_DATA_BUCKET"))

    routes = [
        ("/watch", "GET", lambda_watch, "watch", "lambda for watching"),
    ]
    m.create_apigw('foobar', routes, opts=ResourceOptions(depends_on=[lambda_watch], replace_on_changes=["*"], delete_before_replace=True))
