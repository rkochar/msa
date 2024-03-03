def confirm_transaction(message):
    sender, receiver, amount = int(message["sender"]), int(message["receiver"]), int(message["amount"])
    print(f"Confirming transaction sender: {sender}, receiver: {receiver}, amount: {amount}")

    accounts = execute_sql_query(["SELECT * FROM bank_account"])[0]
    old_sender, old_receiver = accounts[sender - 1][1:3], accounts[receiver - 1][1:3]

    if int(old_sender[1]) < amount:
        print(f"Insufficient funds: sender: {sender}, receiver: {receiver}, amount: {amount}")
    else:
        current_sender = (int(old_sender[0]) + 1, int(old_sender[1]) - amount)
        current_receiver = (int(old_receiver[0]) + 1, int(old_receiver[1]) + amount)

        queries = [
            f"UPDATE bank_account SET current_version = {current_sender[0]}, amount = {current_sender[1]}, previous_version = {old_sender[0]}, previous_amount = {old_sender[1]} WHERE id = {sender}",
            f"UPDATE bank_account SET current_version = {current_receiver[0]}, amount = {current_receiver[1]}, previous_version = {old_receiver[0]}, previous_amount = {old_receiver[1]} WHERE id = {receiver}",
            f"UPDATE bank_account_{sender} SET current_version = {current_sender[0]}, amount = {current_sender[1]}, previous_version = {old_sender[0]}, previous_amount = {old_sender[1]} WHERE id = {sender}",
            f"UPDATE bank_account_{receiver} SET current_version = {current_receiver[0]}, amount = {current_receiver[1]}, previous_version = {old_receiver[0]}, previous_amount = {old_receiver[1]} WHERE id = {receiver}"
        ]
        execute_sql_query(queries)
