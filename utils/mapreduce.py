# Adapted from https://github.com/awslabs/lambda-refarch-mapreduce

import json
import logging

from pulumi import ResourceOptions
from utils.monad import Monad

logging.basicConfig(level='WARNING')
config = json.loads(open('serverless_code/common/mapreduce/start/helpers/driverconfig.json', 'r').read())
job_bucket, result_bucket, L_PREFIX, job_id = config["jobBucket"], config["resultBucket"], "BL", "bl-release"
mapper_lambda_name, reducer_lambda_name, rc_lambda_name = L_PREFIX + "-mapper-" + job_id, L_PREFIX + "-reducer-" + job_id, L_PREFIX + "-rc-" + job_id


def mapreduce():
    m = Monad()

    lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-basic-role", "lambda-role-attachment", "lambda-s3-policy", "mapreduce/lambda-s3-policy")
    mapper_queue, mapper_environment = m.create_message_queue("mapper", fifo=False, message_retention_seconds="150s")
    lambda_mapper = m.create_lambda(mapper_lambda_name, "mapreduce/mapper", "mapper.lambda_handler", role=lambda_iam_role, template="mq_s3", mq_topic=mapper_queue, environment=mapper_environment | {"QUEUE_NAME": "mapper"}, ram=config["lambdaMemory"], timeout_seconds=150)
    lambda_start = m.create_lambda("start","mapreduce/start", "driver.lambda_handler", role=lambda_iam_role, template="http_s3_pub", environment=mapper_environment | {"QUEUE_NAME": "mapper"}, timeout_seconds=150)  # To scale better, this should be broken into a start and collect at end with eventbridge cron
    lambda_result = m.create_lambda("result", "mapreduce/result", "result.lambda_handler", role=lambda_iam_role, template="http_s3", environment={"resultBucket": result_bucket, "jobId": job_id}, timeout_seconds=30)

    reducer_queue, reducer_environment = m.create_message_queue("reducer", fifo=False, message_retention_seconds="150s")
    lambda_reducer = m.create_lambda(reducer_lambda_name, "mapreduce/reducer", "reducer.lambda_handler", role=lambda_iam_role, template="mq_s3", mq_topic=reducer_queue, environment=reducer_environment, ram=config["lambdaMemory"], timeout_seconds=150)
    reducer_coord_prefix = job_id + "/task"
    lambda_rc = m.create_lambda(rc_lambda_name, "mapreduce/reducer-coordinator", "reducercoordinator.lambda_handler", role=lambda_iam_role, template="s3_s3_pub", bucket=(job_bucket, reducer_coord_prefix), environment=reducer_environment, ram=config["lambdaMemory"], timeout_seconds=150)

    routes = [
        ("/start", "POST", lambda_start, "start", "Driver lambda that starts mapreduce"),
        ("/result", "GET", lambda_result, "result", "Get result of mapreduce")
    ]
    apigw = m.create_apigw('mapreduce', routes, opts=ResourceOptions(depends_on=[lambda_mapper, lambda_reducer], replace_on_changes=["*"], delete_before_replace=True))
