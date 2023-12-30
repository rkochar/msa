import sqlalchemy

from google.cloud.sql.connector import Connector, IPTypes


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


if __name__ == '__main__':
    pool = connect("master-thesis-faas-monad:europe-west1:foobar", "foouser", "foopass123", "foobar")
    print("connected")

    with pool.connect() as db_conn:
        db_conn.execute(
            sqlalchemy.text(
                "CREATE TABLE IF NOT EXISTS bank_account"
                "( id SERIAL NOT NULL, current_version INT NOT NULL, amount INT NOT NULL,"
                "previous_version INT, previous_amount INT,"
                "PRIMARY KEY (id) )"
            )
        )
        db_conn.commit()
        insp = sqlalchemy.inspect(pool)
        print(f"tables: {insp.get_table_names()}")

        init_statement = sqlalchemy.text(
            "INSERT INTO bank_account (current_version, amount) VALUES (:current_version, :amount)"
        )
        for _ in range(5):
            db_conn.execute(init_statement, parameters={"current_version": 0, "amount": 10})
        db_conn.commit()

        # insert_statement = sqlalchemy.text(
        #     "INSERT INTO foobar (sender, receiver, amount) VALUES (:sender, :receiver, :amount)"
        # )
        #
        # db_conn.execute(insert_statement, parameters={"sender": 1, "receiver": 2, "amount": 100})
        # db_conn.execute(insert_statement, parameters={"sender": 2, "receiver": 1, "amount": 10})
        # db_conn.execute(insert_statement, parameters={"sender": 4, "receiver": 2, "amount": 50})
        # db_conn.commit()

        results = db_conn.execute(sqlalchemy.text("SELECT * FROM bank_account")).fetchall()

        print("results")
        for row in results:
            print(row)
        db_conn.close()

# https://stackoverflow.com/questions/73493052/how-to-connect-to-cloud-sql-using-python
# https://cloud.google.com/blog/topics/developers-practitioners/how-connect-cloud-sql-using-python-easy-way
