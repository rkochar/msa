import sqlalchemy
import functions_framework
from google.cloud.sql.connector import Connector, IPTypes
from os import getenv
from base64 import b64decode

pool = None

@functions_framework.cloud_event
def template(cloud_event):
    message = b64decode(cloud_event.data["message"]["data"]).decode("utf-8")

    global pool
    pool = connect(getenv('INSTANCE_CONNECTION_NAME'), getenv("USERNAME"), getenv("PASSWORD"), getenv("DATABASE_NAME"))

    body = ""


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
