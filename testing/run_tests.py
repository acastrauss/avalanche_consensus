import unittest

from testing.node.dag_test import TestDag
from testing.node.node_key_test import TestNodeKey


def tests():
    suite = unittest.TestSuite()
    
    suite.addTest(TestNodeKey('test_KeyCreation'))

    suite.addTest(TestDag('test_GetValidatedTransactions'))
    suite.addTest(TestDag('test_InsertTransaction'))
    suite.addTest(TestDag('test_TransactionNotInDag'))
    suite.addTest(TestDag('test_FindConflicting'))
