import copy
import unittest

from models.node.model_defines import DECISION_THRESHOLD
from models.node.node_key import NodeKey
from models.transaction.transaction import Transaction
from models.transaction.verification_data import (ConsensusResult,
                                                  VerificationData)
from testing.helpers.account_generator import GetRandomAccount, GetRandomAmount
from testing.helpers.transaction_generator import (MAX_AMOUNT_TRANSACTION,
                                                   MIN_AMOUNT_TRANSACTION)


class TestTransaction(unittest.TestCase):
    def test_SignTransaction(self):
        nodeKey = NodeKey()
        transaction = Transaction(
            GetRandomAccount(), GetRandomAccount(), 
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
    
        transaction.SignTransaction(nodeKey.PrivateKey)
        verifiedSignature = transaction.VerifyTransactionSignature(nodeKey.PublicKey)
        self.assertTrue(verifiedSignature)

        falseKey = NodeKey()
        verifiedSignature = transaction.VerifyTransactionSignature(falseKey.PublicKey)
        self.assertFalse(verifiedSignature)

    def test_VerifyTransaction(self):
        nodeKey = NodeKey()

        t1 = Transaction(
            GetRandomAccount(), GetRandomAccount(), 
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )

        t1.SignTransaction(nodeKey.PrivateKey)
        self.assertTrue(t1.VerifyTransactionSignature(nodeKey.PublicKey))
        falseKey = NodeKey()
        t2 = Transaction(
            GetRandomAccount(), GetRandomAccount(), 
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t2.SignTransaction(falseKey.PrivateKey)
        self.assertFalse(t2.VerifyTransactionSignature(nodeKey.PublicKey))

    def test_HaveDirectChild(self):
        t1 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t2 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )

        t1.Children.append(t2)
        self.assertTrue(t1.HaveDirectChild(t2))

        t1.Children.remove(t2)
        self.assertFalse(t1.HaveDirectChild(t2))

    def test_IsConflicted(self):
        t1 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t2 = copy.deepcopy(t1)
        t2.Id += 1
        self.assertTrue(t1.IsConflicted(t2))
        t1.Children.append(t2)
        self.assertFalse(t1.IsConflicted(t2))
        
    def test_IsMyAncestor(self):
        t1 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t2 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t3 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t4 = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        t1.Children.append(t2)
        t2.Children.append(t3)
        self.assertTrue(t1.IsMyAncestor(t2))
        self.assertTrue(t1.IsMyAncestor(t3))
        self.assertFalse(t1.IsMyAncestor(t4))
             
    def test_ResolveConsensusResult(self):
        t = Transaction(
            GetRandomAccount(), GetRandomAccount(),
            GetRandomAmount(MIN_AMOUNT_TRANSACTION, MAX_AMOUNT_TRANSACTION)
        )
        preResultVerificationData: VerificationData = copy.deepcopy(t.VerificationData)
        t.ResolveConsensusResult(ConsensusResult.ACCEPTED)
        self.assertTrue(t.VerificationData.Chit)
        self.assertEqual(preResultVerificationData.Confidence + 1, t.VerificationData.Confidence)
        self.assertEqual(preResultVerificationData.ConsecutiveSuccesses + 1, t.VerificationData.ConsecutiveSuccesses)

        t.VerificationData.ConsecutiveSuccesses = DECISION_THRESHOLD
        t.ResolveConsensusResult(ConsensusResult.ACCEPTED)
        self.assertTrue(t.VerificationData.Validated)

        t.ResolveConsensusResult(ConsensusResult.REJECTED_FOR_ANOTHER)
        self.assertEqual(t.VerificationData.ConsecutiveSuccesses, 1)
        t.ResolveConsensusResult(ConsensusResult.NONE_ACCEPTED)
        self.assertEqual(t.VerificationData.ConsecutiveSuccesses, 0)
