import sqlalchemy
import functions_framework
from google.cloud.sql.connector import Connector, IPTypes
from os import getenv


pool = None

@functions_framework.http
def template(request):
    query_string_parameters = request.args
    headers = request.headers

    instance_connection_name, dbname, username, password = getenv('INSTANCE_CONNECTION_NAME'), getenv(
        "DATABASE_NAME"), getenv("USERNAME"), getenv("PASSWORD")
    global pool
    pool = connect(instance_connection_name, username, password, dbname)

    body = ""

    return body


def connect(instance_connection, username, password, dbname):
    def getconn():
        conn = Connector().connect(
            instance_connection,
            "pymysql",
            user=username,
            password=password,
            db=dbname
        )
        return conn

    return sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn
    )


def execute_sql_query(queries):
    global pool
    with pool.connect() as db_conn:
        results = []
        for query in queries:
            if "SELECT" in query.upper():
                results.append(db_conn.execute(sqlalchemy.text(query)).fetchall())
            else:
                results.append(db_conn.execute(sqlalchemy.text(query)))
        db_conn.commit()
        return results
