from models.transaction.transaction import Transaction


class SendingTransaction:
    def __init__(self, transaction: Transaction, senderPublicKey) -> None:
        self.Transaction = transaction
        self.SenderPublicKey = senderPublicKey