
import asyncio
import copy
import random

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from models.node.dag import DAG
from models.node.model_defines import *
from models.node.node_key import NodeKey
from models.transaction.sending_transaction import SendingTransaction
from models.transaction.transaction import Transaction
from models.transaction.verification_data import ConsensusResult


class TransactionCount:
    def __init__(self, transaction: Transaction) -> None:
        self.Transaction = transaction
        self.Count = 1        


class Node:
    NODE_ID = 0
    def __init__(self) -> None:
        self.Participants = []
        self.Weight = 0
        self.Key = NodeKey()
        self.DAG = DAG()
        self.Id = Node.NODE_ID
        Node.NODE_ID += 1
        
    def GetValidatedTransactions(self):
        return self.DAG.GetValidatedTransactions()    

    async def TryVerifyingTransaction(self, transaction: SendingTransaction):
        if transaction.Transaction.IsValidated():
            return transaction.Transaction
        else:
            isValidSignature = self.__IsSignatureValid__(transaction)
            isValidAmount = self.__IsAmountValid__(transaction.Transaction)
            validAccounts = self.__AreAccountsValid__(transaction.Transaction)

            if isValidAmount and isValidSignature and validAccounts:
                conflicting = self.__FindConflicting__(transaction.Transaction)
                if conflicting is None:
                    return transaction.Transaction
                else:
                    return conflicting
            else:
                return None

    def __VerifyWitouthKey__(self, transaction: Transaction):
        if transaction.IsValidated():
            return transaction
        else:
            isValidAmount = self.__IsAmountValid__(transaction)
            validAccounts = self.__AreAccountsValid__(transaction)
            if isValidAmount and validAccounts:
                conflicting = self.__FindConflicting__(transaction)
                if conflicting is None:
                    return transaction
                else:
                    return conflicting
            else:
                return None

    def __IsSignatureValid__(self, transaction: SendingTransaction):
        try:
            transaction.SenderPublicKey.verify(
                transaction.Transaction.GetSignature(),
                transaction.Transaction.GetBytes(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature as ise:
            return False

    def __IsAmountValid__(self, transaction: Transaction):
        return transaction.IsAmountValid()

    def __AreAccountsValid__(self, transaction: Transaction):
        return transaction.AreAccountsValid()

    def __FindConflicting__(self, transaction: Transaction):
        return self.DAG.FindConflicting(transaction)

    async def RunConsensus(self, transaction: Transaction):
        localTransaction = copy.deepcopy(transaction)

        myValidation = self.__VerifyWitouthKey__(localTransaction)

        if myValidation is None:
            return

        myPreference = localTransaction

        queriesCnt = 0

        while (not myPreference.IsValidated()):
            queriesCnt += 1
            
            queryingTask = asyncio.create_task(self.__QueryNodesAboutTransaction__(myPreference))
            queryingResults = await queryingTask

            if len(queryingResults.keys()) == 0:
                myPreference.ResolveConsensusResult(ConsensusResult.NONE_ACCEPTED)
                continue

            votedTransactionId = max(queryingResults, key=queryingResults.get)
            votedTransaction = queryingResults[votedTransactionId].Transaction

            if queryingResults[votedTransactionId].Count >= QUORUM_SIZE:
                if votedTransaction == myPreference:
                    myPreference.ResolveConsensusResult(ConsensusResult.ACCEPTED)
                else:
                    myPreference.ResolveConsensusResult(ConsensusResult.REJECTED_FOR_ANOTHER)
                    myPreference = votedTransaction
            else:
                myPreference.ResolveConsensusResult(ConsensusResult.NONE_ACCEPTED)
            
        self.Weight += 1
        self.DAG.InsertTransaction(myPreference)
    
    async def __QueryNodesAboutTransaction__(self, transaction: Transaction):
        transaction.SignTransaction(self.Key.PrivateKey)
        sendingTransaction = SendingTransaction(transaction, self.Key.PublicKey)
        selectedParticipants = random.sample(self.Participants, SAMPLE_SIZE)
        queryResults = {}
        queryingTasks = []

        for p in selectedParticipants:
            queryingTasks.append(asyncio.create_task(p.TryVerifyingTransaction(sendingTransaction)))
            
        results = await asyncio.gather(*queryingTasks)

        for r in results:    
            queryResponse = r
            if queryResponse is not None:
                if queryResponse.Id in queryResults.keys():
                    queryResults[queryResponse.Id].Count += 1
                else:
                    queryResults[queryResponse.Id] = TransactionCount(queryResponse)

        return queryResults