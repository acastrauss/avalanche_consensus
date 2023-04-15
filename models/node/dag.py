from models.transaction.transaction import Transaction


class DAG:
    def __init__(self) -> None:
        self.Roots = []
        self.TransactionAdded = False

    def GetValidatedTransactions(self):
        retval = []

        for r in self.Roots:
            if r.IsValidated():
                validatedChildren = self.__GetValidatedForRoot__(r)
                retval.extend(validatedChildren)

        return retval

    def __GetValidatedForRoot__(self, root: Transaction):
        retval = []

        if root.IsValidated():
            retval.append(root)

            for c in root.Children:
                retval.extend(self.__GetValidatedForRoot__(c))

        return retval

    def InsertTransaction(self, transaction: Transaction):
        self.TransactionAdded = False
        if len(self.Roots) == 0:
            self.Roots.append(transaction)
            self.TransactionAdded = True
        else:
            for r in self.Roots:
                self.__AddTransactionToAllAncestors__(r, transaction)
                if self.TransactionAdded:
                    break
            
            rootIds = [r.Id for r in self.Roots]
            if (not self.TransactionAdded) and (transaction.Id not in rootIds):
                self.Roots.append(transaction)

    def __AddTransactionToAllAncestors__(self, root: Transaction, transaction: Transaction):
        if root.Id == transaction.Id:
            # print("Transaction already in DAG")
            return

        if (root.Id in transaction.GetParentIds()) and (not root.HaveDirectChild(transaction)):
            root.AddChild(transaction)
            transaction.AddParent(root)
            self.TransactionAdded = True
        elif root.IsMyAncestor(transaction):
            for c in root.Children:
                self.__AddTransactionToAllAncestors__(c, transaction)
                if self.TransactionAdded:
                    break

    def IsTransactionInDAG(self, transaction: Transaction):
        inDAG = False
        for r in self.Roots:
            inDAG |= self.__IsTransactionInSubGraph__(r, transaction)
            if inDAG:
                return inDAG
        return False

    def __IsTransactionInSubGraph__(self, root: Transaction, transaction: Transaction):
        isChild = False
        if root.Id == transaction.Id:
            isChild = True
        elif root.Children:
            isChild = False
            for c in root.Children:
                isChild |= self.__IsTransactionInSubGraph__(c, transaction)
                if isChild:
                    break   
        else:
            isChild = False
        return isChild

    def FindConflicting(self, transaciton: Transaction):
        for r in self.Roots:
            rootConfl = self.__CheckForConflicting__(r, transaciton)
            if rootConfl is not None:
                return rootConfl
        return None

    def __CheckForConflicting__(self, root: Transaction, possibleConflitcingTransaction: Transaction):
        if root.IsConflicted(possibleConflitcingTransaction):
            return root
        elif root.Children:
            for c in root.Children:
                return self.__CheckForConflicting__(c, possibleConflitcingTransaction)
        return None