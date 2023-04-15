import copy
import unittest

from models.node.dag import DAG
from models.transaction.transaction import Transaction
from testing.helpers.account_generator import *
from testing.helpers.transaction_generator import *


class InitDAGTransaction():
    ACCOUNTS_TO_CREATE = 4
    TRANSACTION_TO_CREATE = NUM_OF_TRANSACTIONS
    def __init__(self) -> None:
        self.Accounts = []
        for i in range(InitDAGTransaction.ACCOUNTS_TO_CREATE):
            self.Accounts.append(GetRandomAccount())

        self.Transactions = []
        for i in range(NUM_OF_TRANSACTIONS):
            accountIndxs = list(range(0, len(self.Accounts) - 1))
            fromAccIndx = random.choice(accountIndxs)
            fromAcc = self.Accounts[fromAccIndx]
            accountIndxs.remove(fromAccIndx)
            toAcc = self.Accounts[random.choice(accountIndxs)]
            transaction = fromAcc.CreateTransactionToAccount(GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION), toAcc)
            self.Transactions.append(transaction)

class TestDag(unittest.TestCase):
    def setUp(self) -> None:
        self.InitData = InitDAGTransaction()
        self.DAG = DAG()

    def test_GetValidatedTransactions(self):
        for t in self.InitData.Transactions:
            self.DAG.InsertTransaction(t)

        nofValidatedTransactions = int(NUM_OF_TRANSACTIONS * 0.3)

        for i in range(nofValidatedTransactions):
            self.InitData.Transactions[i].VerificationData.Validated = True

        validatedInDag = self.DAG.GetValidatedTransactions()

        self.assertEqual(len(validatedInDag), nofValidatedTransactions)

    def test_InsertTransaction(self):
        for t in self.InitData.Transactions:
            self.DAG.InsertTransaction(t)
            self.assertTrue(self.DAG.IsTransactionInDAG(t))

    def test_TransactionNotInDag(self):
        fakeTransaction = Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION))
        self.assertFalse(self.DAG.IsTransactionInDAG(fakeTransaction))

        for t in self.InitData.Transactions:
            self.DAG.InsertTransaction(t)

        fakeTransaction = Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION))
        self.assertFalse(self.DAG.IsTransactionInDAG(fakeTransaction))

    def test_FindConflicting(self):
        t1 = self.InitData.Transactions[0]
        tConflicting = copy.deepcopy(t1)
        tConflicting.Id += 1
        self.DAG.InsertTransaction(t1)
        foundConflicting = self.DAG.FindConflicting(tConflicting)
        self.assertIsNotNone(foundConflicting)
        self.assertEqual(foundConflicting.Id, t1.Id)

        notConflicting = self.DAG.FindConflicting(Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MIN_AMOUNT_ACCOUNT_CREATION, MAX_AMOUNT_ACCOUNT_CREATION)))
        self.assertIsNone(notConflicting)
        