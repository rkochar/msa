from pulumi import ResourceOptions
from utils.monad import Monad


def create_mvccdb():
    m = Monad()

    sqldb, sqldb_lambda_environment = m.create_sql_database("sqldb", "mysql", "8.0.34", 10, "foouser", "foopass123", "small")

    sql_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-basic-role", "sql-attachment", "sql-policy", "mq-sql-policy")
    sql_init_lambda = m.create_lambda('sqldb-init', "mvccdb/init", "mvcc_sqldb_init.sqldb_init", template="http_sql", environment=sqldb_lambda_environment, role=sql_lambda_iam_role, imports=["pymysql"], is_timed=False, span=False, opts=ResourceOptions(depends_on=[sqldb]))
    sql_get_lambda = m.create_lambda('sqldb-get', "mvccdb/get", "mvcc_sqldb_get.sqldb_get", template="http_sql", environment=sqldb_lambda_environment, role=sql_lambda_iam_role, imports=["pymysql", "pydantic"], is_timed=True, span=False, opts=ResourceOptions(depends_on=[sqldb]))

    # Worker
    transaction_mq, worker_environment = m.create_message_queue(topic_name='transaction')
    mq_sql_lambda_iam_role = m.create_iam("apigw-lambda-iam-role", "lambda-basic-role", "mq-sql-attachment", "mq-sql-policy", "mq-sql-policy")
    worker_lambda = m.create_lambda('worker', "mvccdb/worker", "worker.check_transaction", template="http_sql_pub",  environment=worker_environment | sqldb_lambda_environment, role=mq_sql_lambda_iam_role, imports=["pymysql", "pydantic"], is_timed=True, span=False, opts=ResourceOptions(depends_on=[sqldb, transaction_mq]))
    control_lambda = m.create_lambda('control', "mvccdb/control", "control.confirm_transaction", template="mq_sql", role=mq_sql_lambda_iam_role, mq_topic=transaction_mq, environment=worker_environment | sqldb_lambda_environment, imports=["pymysql"], is_timed=False, span=True, opts=ResourceOptions(depends_on=[transaction_mq, sqldb, worker_lambda]))

    routes = [
        ("/init", "GET", sql_init_lambda, "sqldb-init", "Setup database or MVCC-DB"),
        ("/send", "GET", worker_lambda, "worker", "Make a transaction"),
        ("/status", "GET", sql_get_lambda, "sqldb-get", "Get the current state of an account")
    ]
    m.create_apigw('mvccdb', routes, opts=ResourceOptions(depends_on=[sql_init_lambda, sql_get_lambda, worker_lambda]))
