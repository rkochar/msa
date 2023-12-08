import pymysql
from sys import exit
from os import getenv


def testsql(event, headers, query_parameters):
    statement = "CREATE TABLE IF NOT EXISTS testsql (id INT NOT NULL AUTO_INCREMENT, name VARCHAR(255) NOT NULL, PRIMARY KEY (id))"
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

    with conn.cursor() as cur:
        cur.execute(statement)
        cur.execute("create table if not exists testsql (id int not null auto_increment, name varchar(255) not null, primary key (id));")
        cur.execute("SELECT * FROM testsql")
        for row in cur:
            print(row)
        conn.commit()
        cur.close()

    return f"Hello from Lambda!"
