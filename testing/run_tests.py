import unittest

from testing.node.dag_test import TestDag
from testing.node.node_key_test import TestNodeKey
from testing.node.node_test import TestNode


def tests():
    suite = unittest.TestSuite()
    
    suite.addTest(TestNodeKey('test_KeyCreation'))

    suite.addTest(TestDag('test_GetValidatedTransactions'))
    suite.addTest(TestDag('test_InsertTransaction'))
    suite.addTest(TestDag('test_TransactionNotInDag'))
    suite.addTest(TestDag('test_FindConflicting'))

    suite.addTest(TestNode('test_TryVerifyingTransactionInvalidAmount'))
    suite.addTest(TestNode('test_TryVerifyingTransactionInvalidAccounts'))
    suite.addTest(TestNode('test_TryVerifyingTransactionInvalidSignature'))
    suite.addTest(TestNode('test_TryVerifyingConflictingTransaction'))
    suite.addTest(TestNode('test_TryVerifyingValidTransaction'))
    suite.addTest(TestNode('test_RunConsensusInvalidTransactions'))
    suite.addTest(TestNode('test_RunConsensusValidTransactions'))

    runner = unittest.runner.TextTestRunner()
    runner.run(suite)