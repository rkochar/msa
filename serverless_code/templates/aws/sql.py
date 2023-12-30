import pymysql
from sys import exit


def connect():
    rds_host, port = getenv("SQLDB_HOST"), int(getenv("SQLDB_PORT"))
    db_name = getenv("SQLDB_DBNAME")
    username, password = getenv("SQLDB_USERNAME"), getenv("SQLDB_PASSWORD")

    try:
        conn = pymysql.connect(host=rds_host,
                               user=username,
                               passwd=password,
                               db=db_name,
                               connect_timeout=5,
                               port=port
                               )
    except pymysql.MySQLError as e:
        print(e)
        exit()
    return conn


def execute_sql_query(queries):
    conn = connect()
    with conn.cursor() as cur:
        results = []
        for query in queries:
            if "SELECT" in query.upper():
                cur.execute(query)
                conn.commit()
                for row in cur:
                    results.append(row)
            else:
                cur.execute(query)
                conn.commit()
        cur.close()
        return [results]
