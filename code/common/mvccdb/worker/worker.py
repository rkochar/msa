from pydantic import BaseModel, Field, ValidationError


def check_transaction(headers, query_parameters):
    try:
        transaction = Transaction(sender=headers.get("sender"), receiver=headers.get("receiver"), amount=headers.get("amount"), strict=False)
    except ValidationError as e:
        return "Errors found: " + str(e.error_count()) + "\n" + str(e.errors())

    print(f"Checking transaction sender: {transaction.sender}, receiver: {transaction.receiver}, amount: {transaction.amount}")

    results = execute_sql_query([f"SELECT * FROM bank_account_{transaction.sender}"])[0]
    print(f"Row_{transaction.sender} fetched: {results}")
    _, current_version, current_amount, previous_version, previous_amount = results[0]

    if current_amount < transaction.amount:
        return "Insufficient funds"
    else:
        return str({"sender": transaction.sender, "receiver": transaction.receiver, "amount": transaction.amount})


class Transaction(BaseModel):
    sender: int = Field(ge=1, le=5)
    receiver: int = Field(ge=1, le=5)
    amount: int = Field(ge=1, le=10)

