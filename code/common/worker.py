def check_transaction(headers, query_parameters):
    sender = int(headers.get("sender")) or -1
    receiver = int(headers.get("receiver")) or -1
    amount = int(headers.get("amount")) or -1

    if sender == -1 or not (1 <= sender <= 5):
        return "Incorrect/missing sender provided"
    if receiver == -1 or not (1 <= sender <= 5):
        return "Incorrect/missing receiver provided"
    if not (0 < amount <= 10):
        return "Incorrect amount provided. 0 < amount <= 10 expected"
    print(f"Checking transaction sender: {sender}, receiver: {receiver}, amount: {amount}")

    results = execute_sql_query([f"SELECT * FROM bank_account_{sender}"])[0]
    print(f"Row_{sender} fetched: {results}")
    _, current_version, current_amount, previous_version, previous_amount = results[0]

    if current_amount < amount:
        return "Insufficient funds"
    else:
        return str({"sender": sender, "receiver": receiver, "amount": amount})
