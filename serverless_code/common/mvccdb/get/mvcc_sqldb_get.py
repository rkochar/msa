def sqldb_get(headers, query_parameters):
    id = query_parameters.get("id") or 0
    worker = headers.get("worker") or -1
    if not (0 <= int(id) <= 5):
        return "Incorrect/missing id provided"

    if int(worker) == 42:
        print("Worker 42")
        results = execute_sql_query([f"SELECT * FROM bank_account_{id}"])[0]
    elif int(id) == 0:
        results = execute_sql_query([f"SELECT * FROM bank_account"])[0]
    else:
        results = execute_sql_query([f"SELECT * FROM bank_account WHERE id = {id}"])[0]
    print(f"Results: {results}")
    return str(results)
