from google.cloud import pubsub_v1
from os import getenv
import functions_framework
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes


pool = None
@functions_framework.http
def template(request):
    query_string_parameters = request.args
    headers = request.headers

    global pool
    pool = connect(getenv('INSTANCE_CONNECTION_NAME'), getenv("USERNAME"), getenv("PASSWORD"), getenv("DATABASE_NAME"))

    body = ""

    future = pubsub_v1.PublisherClient().publish(getenv("TOPIC_ID"), bytes(body, "utf-8"))
    return future.result()


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
