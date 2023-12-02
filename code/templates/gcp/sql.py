import sqlalchemy
from google.cloud.sql.connector import Connector


def connect(instance_connection, username, password, dbname):
    def getconn():
        conn = Connector().connect(
            instance_connection,
            driver="pymysql",
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
    instance_connection_name, dbname, username, password = getenv('INSTANCE_CONNECTION_NAME'), getenv(
        "DATABASE_NAME"), getenv("SQLDB_USERNAME"), getenv("SQLDB_PASSWORD")
    pool = connect(instance_connection_name, username, password, dbname)

    with pool.connect() as db_conn:
        results = []
        for query in queries:
            if "SELECT" in query.upper():
                results.append(db_conn.execute(sqlalchemy.text(query)).fetchall())
            else:
                results.append(db_conn.execute(sqlalchemy.text(query)))
        db_conn.commit()
        return results
