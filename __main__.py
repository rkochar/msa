from utils.foobar import apigw_foobar
from utils.mq import create_mq
from utils.mvccdb import create_mvccdb
from utils.chain import chain

# apigw_foobar()
# create_mq()
# chain()
# create_mvccdb()

from utils.monad import Monad

m = Monad()
sqldb, sqldb_lambda_environment = m.create_sql_database("testsql", "mysql", "8.0.34", 10, "foouser", "foopass123", "small")
apigw_lambda_iam_role = m.create_iam("a-lambda-iam-role", "lambda-role", "lambda-role-attachment", "logs-policy", "sql-role")  # TODO: make a log policy
lambda_foo = m.create_lambda('testsql', "testsql.testsql", template="http_sql", role=apigw_lambda_iam_role)
