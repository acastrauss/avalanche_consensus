
import asyncio
import random
import string
from datetime import datetime
from threading import Thread

from models.node.model_defines import NOF_PARTICIPANTS
from models.node.node import Node
from models.transaction.account import Account
from models.transaction.amount import Amount
from models.transaction.transaction import Transaction

NUM_OF_ACCOUNTS = 10
ACCOUNT_NUM_LENGTH = 20
NUM_OF_TRANSACTIONS = 100

def GetRandomString(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

MIN_AMOUNT_ACCOUNT_CREATION = 1000
MAX_AMOUNT_ACCOUNT_CREATION = 10000

MIN_AMOUNT_TRANSACTION = 10
MAX_AMOUNT_TRANSACTION = 100

def GetRandomAmount(min, max):
    return Amount(random.uniform(min, max))

async def main():
    accounts = []
    for i in range(NUM_OF_ACCOUNTS):
        accounts.append(Account(GetRandomString(ACCOUNT_NUM_LENGTH), GetRandomAmount(MIN_AMOUNT_ACCOUNT_CREATION, MAX_AMOUNT_ACCOUNT_CREATION)))

    validators = []

    for i in range(NOF_PARTICIPANTS):
        validators.append(Node())

    for v in validators:
        v.Participants = [p for p in validators if p.Id != v.Id ]

    transactions: list[Transaction] = []
    verificationTasks = []

    for i in range(NUM_OF_TRANSACTIONS):
        accountIndxs = list(range(0, len(accounts) - 1))
        fromAccIndx = random.choice(accountIndxs)
        fromAcc = accounts[fromAccIndx]
        accountIndxs.remove(fromAccIndx)
        toAcc = accounts[random.choice(accountIndxs)]
        t = fromAcc.CreateTransactionToAccount(
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION),
            toAcc
        )
        transactions.append(t)

        verificationTasks.append(asyncio.create_task(validators[random.randint(0, len(validators) - 1)].RunConsensus(transactions[i])))
        
    await asyncio.gather(*verificationTasks)

    invalidTransaction = Transaction(
        accounts[0], accounts[1], Amount(MAX_AMOUNT_ACCOUNT_CREATION * 1000)
    )
    transactions.append(invalidTransaction)
    invalidTransactionTask = asyncio.create_task(validators[0].RunConsensus(invalidTransaction))
    await invalidTransactionTask

    validatedTransaction = []

    for v in validators:
        validatedTransaction.extend(v.GetValidatedTransactions())

    print(f"Percentage of validated: {len(validatedTransaction) / len(transactions) * 100}")

if __name__ == "__main__":
    asyncio.run(main())