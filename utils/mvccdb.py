from utils.monad import Monad
from pulumi import ResourceOptions


def create_mvccdb():
    m = Monad()

    # SQL database to confirm transactions
    sqldb, sqldb_lambda_environment = m.create_sql_database("foobar", "mysql", "8.0.34", 10, "foouser", "foopass123", "small")

    apigw_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-basic-role")
    sql_init_lambda = m.create_lambda('sqldb-init', "mvcc_sqldb_init.sqldb_init", template="http_sql",
                                      environment=sqldb_lambda_environment, role=apigw_lambda_iam_role)
    sql_get_lambda = m.create_lambda('sqldb-get', "mvcc_sqldb_get.sqldb_get", template="http_sql",
                                     environment=sqldb_lambda_environment, role=apigw_lambda_iam_role)

    # Worker
    transaction_mq, worker_environment = m.create_message_queue(topic_name='transaction')
    mq_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-basic-role",
                                      "lambda-role-attachment", "mq-policy", "message-queue-policy")
    worker_lambda = m.create_lambda('worker', "worker.check_transaction", template="http_sql_pub",
                                    environment=worker_environment | sqldb_lambda_environment,
                                    role=mq_lambda_iam_role, opts=ResourceOptions(depends_on=[transaction_mq]))
    control_lambda = m.create_lambda('control', "control.confirm_transaction", template="mq_sql",
                                     role=mq_lambda_iam_role, mq_topic=transaction_mq,
                                     environment=worker_environment | sqldb_lambda_environment,
                                     opts=ResourceOptions(depends_on=[transaction_mq, sqldb]))

    # TODO: remove SNS

    routes = [
        ("/init", "GET", sql_init_lambda, "sqldb-init", "Setup database or MVCC-DB"),
        ("/send", "GET", worker_lambda, "worker", "Make a transaction"),
        ("/status", "GET", sql_get_lambda, "sqldb-get", "Get the current state of an account")
    ]
    m.create_apigw('apigw', routes, opts=ResourceOptions(depends_on=[sql_init_lambda, sql_get_lambda, worker_lambda]))
