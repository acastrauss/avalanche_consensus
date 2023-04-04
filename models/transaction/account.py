from models.transaction.amount import Amount
from models.transaction.transaction import Transaction


class Account:
    def __init__(self, accountNum: str, balance: Amount) -> None:
        self.AccountNum = accountNum
        self.Balance = balance
        self.LastTransaction = None
    
    def CreateTransactionToAccount(self, amount: Amount, accountTo):
        t = Transaction(self, accountTo, amount)
        if self.LastTransaction is not None:
            t.AddParentId(self.LastTransaction.Id)
        self.LastTransaction = t
        return t
