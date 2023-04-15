import asyncio
import copy
import random
import unittest

from models.node.model_defines import NOF_PARTICIPANTS
from models.node.node import Node
from models.node.node_key import NodeKey
from models.transaction.account import Account
from models.transaction.sending_transaction import SendingTransaction
from models.transaction.transaction import Transaction
from testing.helpers.account_generator import (MAX_AMOUNT_ACCOUNT_CREATION,
                                               GetRandomAccount,
                                               GetRandomAmount)
from testing.helpers.transaction_generator import (MAX_AMOUNT_TRANSACTION,
                                                   MIN_AMOUNT_TRANSACTION)


class TestNode(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.Validators: list[Node] = []
        for i in range(2):
            n = Node()
            self.Validators.append(n)
        
        for v in self.Validators:
            otherValidators = list(filter(lambda x: x.Id != v.Id, self.Validators))
            v.Participants = otherValidators
    
    async def test_TryVerifyingTransactionInvalidAmount(self):
        transactionInvalidAmount = Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MAX_AMOUNT_ACCOUNT_CREATION * 10, MAX_AMOUNT_ACCOUNT_CREATION * 20))
        transactionInvalidAmount.SignTransaction(self.Validators[0].Key.PrivateKey)
        invalidAmountSendingTransaction = SendingTransaction(transactionInvalidAmount, self.Validators[0].Key.PublicKey)
        await (asyncio.create_task(self.test_TryVerifyInvalidTransaction(invalidAmountSendingTransaction)))

    async def test_TryVerifyingTransactionInvalidAccounts(self):
        acc = GetRandomAccount()
        tInvalidAccounts = Transaction(acc, acc, GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION))
        tInvalidAccounts.SignTransaction(self.Validators[0].Key.PrivateKey)
        sendingTInvalidAccounts = SendingTransaction(tInvalidAccounts, self.Validators[0].Key.PublicKey)
        await (asyncio.create_task(self.test_TryVerifyInvalidTransaction(sendingTInvalidAccounts)))

    async def test_TryVerifyingTransactionInvalidSignature(self):
        tInvalidSignature = Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION))
        newKey = NodeKey()
        self.Validators[0].Key.PrivateKey = newKey.PrivateKey
        tInvalidSignature.SignTransaction(self.Validators[0].Key.PrivateKey)
        await (asyncio.create_task(self.test_TryVerifyInvalidTransaction(SendingTransaction(tInvalidSignature, self.Validators[0].Key.PublicKey))))

    async def test_TryVerifyInvalidTransaction(self, sendingTransaction: SendingTransaction):
        verifiedTask = asyncio.create_task(self.Validators[1].TryVerifyingTransaction(sendingTransaction))
        verified = await verifiedTask
        self.assertIsNone(verified)

    async def test_TryVerifyingConflictingTransaction(self):
        t1 = Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION))
        self.Validators[0].DAG.InsertTransaction(t1)
        conflicting = copy.deepcopy(t1)
        conflicting.Id += 1

        conflicting.SignTransaction(self.Validators[0].Key.PrivateKey)
        conflictingSendingTransaction = SendingTransaction(conflicting, self.Validators[0].Key.PublicKey)

        verifiedTask = asyncio.create_task(self.Validators[0].TryVerifyingTransaction(conflictingSendingTransaction))
        verified = await verifiedTask
        self.assertIsNotNone(verified)
        self.assertEqual(verified.Id, t1.Id)

    async def test_TryVerifyingValidTransaction(self):
        accFrom = GetRandomAccount()
        accTo = GetRandomAccount()

        for i in range(2):
            t = accFrom.CreateTransactionToAccount(GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION), accTo)
            t.SignTransaction(self.Validators[0].Key.PrivateKey)
            sendingTransaction = SendingTransaction(t, self.Validators[0].Key.PublicKey)

            verified = await (asyncio.create_task(self.Validators[1].TryVerifyingTransaction(sendingTransaction)))
            self.assertIsNotNone(verified)
            self.assertEqual(verified.Id, t.Id)
    
    async def test_RunConsensusInvalidTransactions(self):
        transactionInvalidAmount = Transaction(GetRandomAccount(), GetRandomAccount(), GetRandomAmount(MAX_AMOUNT_ACCOUNT_CREATION * 10, MAX_AMOUNT_ACCOUNT_CREATION * 20))
        consensusRes = await (asyncio.create_task(self.Validators[0].RunConsensus(transactionInvalidAmount)))
        self.assertIsNone(consensusRes)
        
        acc = GetRandomAccount()
        tInvalidAccounts = Transaction(acc, acc, GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION))
        consensusRes = await (asyncio.create_task(self.Validators[0].RunConsensus(tInvalidAccounts)))
        self.assertIsNone(consensusRes)
        
    async def test_RunConsensusValidTransactions(self):
        self.Validators.clear()
        for i in range(NOF_PARTICIPANTS):
            n = Node()
            self.Validators.append(n)
        
        for v in self.Validators:
            otherValidators = list(filter(lambda x: x.Id != v.Id, self.Validators))
            v.Participants = otherValidators

        accounts: list[Account] = []
        nofAccouts = 3
        for i in range(nofAccouts):
            accounts.append(GetRandomAccount())

        nofTransactions = 10
        consesusTasks = []

        for i in range(nofTransactions):
            accountIndxs = list(range(0, len(accounts) - 1))
            fromAccIndx = random.choice(accountIndxs)
            fromAcc = accounts[fromAccIndx]
            accountIndxs.remove(fromAccIndx)
            toAcc = accounts[random.choice(accountIndxs)]
            transaction = fromAcc.CreateTransactionToAccount(GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION), toAcc)
            consesusTasks.append(asyncio.create_task(self.Validators[random.randint(0, len(self.Validators) - 1)].RunConsensus(transaction)))
            
        results = await asyncio.gather(*consesusTasks)

        for r in results:
            self.assertIsNotNone(r)
        
        validatedTransactions = []
        for v in self.Validators:
            validatedTransactions.extend(v.GetValidatedTransactions())

        self.assertEqual(len(validatedTransactions), nofTransactions)

