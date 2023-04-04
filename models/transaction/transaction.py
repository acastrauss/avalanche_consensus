import threading
from datetime import datetime

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from models.node.model_defines import DECISION_THRESHOLD
from models.transaction.amount import Amount
from models.transaction.verification_data import (ConsensusResult,
                                                  VerificationData)


class Transaction:
    TRANSACTION_ENCODING = 'UTF-8'
    TRANSACTION_ID = 0
    TRANSACTION_ALLOWED_TIME_DIFFERENCE_MILLISECONDS = 20
    def __init__(self, accountFrom, accountTo, amount: Amount) -> None:
        self.AccountFrom = accountFrom
        self.AccountFromStateBeforeTransaction = accountFrom.Balance
        self.AccountTo = accountTo
        self.AccountToStateBeforeTransaction = accountTo.Balance
        self.Amount = amount
        self.IsSigned = False
        self.Id = Transaction.TRANSACTION_ID
        Transaction.TRANSACTION_ID += 1
        self.Children = []
        self.Parents = []
        self.ParentIds = []
        self.VerificationData = VerificationData()

    def AddParentId(self, parentId: int):
        
        self.ParentIds.append(parentId)
        

    def AddChild(self, childTransaction):
        
        self.Children.append(childTransaction)
        

    def AddParent(self, parentTransaction):
        
        self.Parents.append(parentTransaction)
        

    def IsValidated(self):
        
        retval = self.VerificationData.Validated
        
        return retval

    def GetSignature(self):
        
        retval = self.Signature
        
        return retval

    def GetBytes(self):
        
        retval = self.TransactionBytes
        
        return retval

    def IsAmountValid(self):
        
        retval = self.AccountFrom.Balance > self.Amount
        
        return retval

    def AreAccountsValid(self):
        
        retval = (self.AccountFrom.AccountNum == self.AccountTo.AccountNum) == False
        
        return retval

    def SignTransaction(self, nodePrivateKey):
        
        self.TransactionBytes = str(self.__dict__).encode(Transaction.TRANSACTION_ENCODING)
        signature = nodePrivateKey.sign(
            self.TransactionBytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        self.Signature = signature
        self.IsSigned = True
        

    def IsConflicted(self, conflictTransaction) -> bool:
        
        retval = (conflictTransaction.Id != self.Id and
            conflictTransaction.AccountFrom.AccountNum == self.AccountFrom.AccountNum and
            conflictTransaction.AccountTo.AccountNum == self.AccountTo.AccountNum and
            conflictTransaction.Amount == self.Amount and
            not self.__IsMyAncestor__(conflictTransaction))
        
        return retval

    def __IsMyAncestor__(self, transaction):
        directAncestor = self.Id in transaction.ParentsIds

        if directAncestor:
            return directAncestor
        else:
            for c in self.Children:
                directAncestor |= c.__IsMyAncestor__(transaction)

        return directAncestor

    def ResolveConsensusResult(self, consesusResult: ConsensusResult):
        
        self.VerificationData.Chit = consesusResult == ConsensusResult.ACCEPTED

        if consesusResult == ConsensusResult.ACCEPTED:
            self.VerificationData.Confidence += 1
            self.VerificationData.ConsecutiveSuccesses += 1
            if self.VerificationData.ConsecutiveSuccesses > DECISION_THRESHOLD:
                self.__ValidateSelf__()
        elif consesusResult == ConsensusResult.REJECTED_FOR_ANOTHER:
            self.VerificationData.ConsecutiveSuccesses = 1
        else:
            self.VerificationData.ConsecutiveSuccesses = 0

        

        for p in self.Parents:
            p.ResolveConsensusResult(consesusResult)

    def __ValidateSelf__(self):
        if not self.VerificationData.Validated:
            self.VerificationData.Validated = True
            self.AccountFrom.Balance = self.AccountFrom.Balance - self.Amount
            self.AccountTo.Balance = self.AccountTo.Balance + self.Amount

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, self.__class__):
            return self.Id == __o.Id
        else:
            return False
