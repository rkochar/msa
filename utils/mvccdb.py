from utils.monad import Monad
from pulumi import ResourceOptions


def create_mvccdb():
    m = Monad()

    # SQL database to confirm transactions
    sqldb, sqldb_lambda_environment = m.create_sql_database("foobar", "mysql", "8.0.34", 10, "foouser", "foopass123",
                                                            "small")

    apigw_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-role")
    sql_init_lambda = m.create_lambda('sqldb-init', "mvcc_sqldb_init.sqldb_init", template="sql",
                                      environment=sqldb_lambda_environment, role=apigw_lambda_iam_role)
    sql_get_lambda = m.create_lambda('sqldb-get', "mvcc_sqldb_get.sqldb_get", template="sql", environment=sqldb_lambda_environment, role=apigw_lambda_iam_role)

    # Worker
    # sqs_transaction, worker_environment = m.create_message_queue(topic_name='transaction')
    # worker_lambda = m.create_lambda("worker", "mvcc_worker.worker", template="sql", environment=worker_environment, role=apigw_lambda_iam_role)

    # lambda_role = m.create_role_policy_attachment("lambda-role-attachment", "sns-policy", "policy/aws/lambda-snssqs.json", "apigw-lambda-iam-role", "policy/aws/lambda-apigw.json")
    #
    # environment = {"SQS_URL": sqs_transaction.url}
    # apigw_lambda_consumer = m.create_lambda('lambda-apigw-consumer', "consumer.consumer", lambda_role, environment, http_trigger=False, topic=sqs_transaction.topic, opts=ResourceOptions(depends_on=[sqs]))
    #
    # apigw_lambda_database = m.create_lambda('lambda-apigw-database', "consumer.consumer", lambda_role, environment, opts=ResourceOptions(depends_on=[sql]))
    #
    routes = [
        ("/init", "GET", sql_init_lambda, "sqldb-init", "Setup database or MVCC-DB"),
        ("/send", "GET", "", "worker", "Make a transaction"),
        ("/status", "GET", sql_get_lambda, "sqldb-get", "Get the current state of an account")
    ]
    m.create_apigw('apigw', routes)
