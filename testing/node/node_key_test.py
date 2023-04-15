import unittest

from models.node.node_key import NodeKey


class TestNodeKey(unittest.TestCase):
    def setUp(self) -> None:
        self.NodeKey = NodeKey()

    def test_KeyCreation(self):
        self.assertIsNotNone(self.NodeKey.PrivateKey)
        self.assertIsNotNone(self.NodeKey.PublicKey)
        self.assertEqual(self.NodeKey.KEY_SIZE, self.NodeKey.PrivateKey.key_size)
        self.assertEqual(self.NodeKey.KEY_SIZE, self.NodeKey.PublicKey.key_size)