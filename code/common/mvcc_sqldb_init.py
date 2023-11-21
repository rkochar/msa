def sqldb_init(pool, headers, query_parameters):
    with pool.connect() as db_conn:
        print("connected")
        db_conn.execute(sqlalchemy.text("DROP TABLE IF EXISTS bank_account"))
        db_conn.execute(
            sqlalchemy.text(
                "CREATE TABLE IF NOT EXISTS bank_account "
                "( id SERIAL NOT NULL, current_version INT NOT NULL, amount INT NOT NULL,"
                "previous_version INT, previous_amount INT,"
                "PRIMARY KEY (id) )"
            )
        )
        db_conn.commit()

        print("created table_i")
        for i in range(5):
            db_conn.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS bank_account_{i}"))
            db_conn.execute(
                sqlalchemy.text(
                    f"CREATE TABLE IF NOT EXISTS bank_account_{i} "
                    "( id SERIAL NOT NULL, current_version INT NOT NULL, amount INT NOT NULL,"
                    "previous_version INT, previous_amount INT,"
                    "PRIMARY KEY (id) )"
                )
            )
        db_conn.commit()

        insert_statement = sqlalchemy.text(
            "INSERT INTO bank_account (current_version, amount) VALUES (:current_version, :amount)"
        )

        print("Setting default values")
        for i in range(5):
            db_conn.execute(
                insert_statement, parameters={"current_version": 0, "amount": 10}
            )
        db_conn.commit()

        print("init finished")
        insp = sqlalchemy.inspect(pool)
        print(f"tables: {insp.get_table_names()}")

        results = db_conn.execute(sqlalchemy.text("SELECT * FROM bank_account")).fetchall()
        db_conn.close()

        print("results")
        return str(results)
