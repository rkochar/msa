from numpy.random import randint
from pydantic import BaseModel, Field, ValidationError, validator


def bar(headers, query_parameters):
    try:
        transaction = Transaction(sender=headers.get("sender"), receiver=headers.get("receiver"), amount=headers.get("amount"))
    except ValidationError as e:
        return f"Errors found: {e.error_count()}. {e.errors()}"
    result = randint(0, 5)
    return f"Transfer {transaction.amount} from {transaction.sender} to {transaction.receiver}. result: {result}"


class Transaction(BaseModel):
    sender: int = Field(ge=1, le=5)
    receiver: int = Field(ge=1, le=5)
    amount: int = Field(ge=1, le=10)

    @validator("receiver")
    def unique_sender_receiver(cls, receiver, values):
        if "sender" in values and receiver == values["sender"]:
            raise ValueError("Sender and receiver must be unique")
        return receiver
