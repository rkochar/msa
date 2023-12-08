def sqldb_init(headers, query_parameters):
    execute_sql_query(["DROP TABLE IF EXISTS bank_account"])
    execute_sql_query(["CREATE TABLE IF NOT EXISTS bank_account ( id SERIAL NOT NULL, current_version INT NOT NULL, amount INT NOT NULL, previous_version INT, previous_amount INT, PRIMARY KEY (id) )"])

    cleanup = []
    for i in range(5):
        cleanup.append(f"DROP TABLE IF EXISTS bank_account_{i}")
        cleanup.append(f"CREATE TABLE IF NOT EXISTS bank_account_{i} ( id INT NOT NULL, current_version INT NOT NULL, amount INT NOT NULL, previous_version INT, previous_amount INT, PRIMARY KEY (id) )")
    execute_sql_query(cleanup)

    queries = []
    for i in range(5):
        queries.append(f"INSERT INTO bank_account_{i} (id, current_version, amount) VALUES ({i}, 0, 10)")
        queries.append(f"INSERT INTO bank_account (current_version, amount) VALUES (0, 10)")

    execute_sql_query(queries)

    results = execute_sql_query(["SELECT * FROM bank_account"])[0]
    print("results")
    return str(results)
