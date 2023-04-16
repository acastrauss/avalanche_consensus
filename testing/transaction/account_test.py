import unittest

from testing.helpers.account_generator import GetRandomAccount, GetRandomAmount
from testing.helpers.transaction_generator import (MAX_AMOUNT_TRANSACTION,
                                                   MIN_AMOUNT_TRANSACTION)


class TestAccount(unittest.TestCase):
    def test_CreatingTransactionFromAccount(self):
        accFrom = GetRandomAccount()
        accTo = GetRandomAccount()
        t1 = accFrom.CreateTransactionToAccount(GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION), accTo)
        self.assertEqual(t1.AccountFrom.AccountNum, accFrom.AccountNum)
        self.assertEqual(t1.AccountTo.AccountNum, accTo.AccountNum)
        self.assertEqual(accFrom.LastTransaction.Id, t1.Id)

        t2 = accFrom.CreateTransactionToAccount(GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION), accTo)
        self.assertEqual(t2.AccountFrom.AccountNum, accFrom.AccountNum)
        self.assertEqual(t2.AccountTo.AccountNum, accTo.AccountNum)
        self.assertEqual(accFrom.LastTransaction.Id, t2.Id)

        self.assertTrue(t2.ParentIds[0], t1.Id)
