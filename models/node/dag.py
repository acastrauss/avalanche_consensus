from models.transaction.transaction import Transaction


class DAG:
    def __init__(self) -> None:
        self.Roots = []
    
    def InsertTransaction(self, transaction: Transaction):
        if len(self.Roots) == 0:
            self.Roots.append(transaction)
        else:
            for r in self.Roots:
                self.__AddTransactionToAllAncestors__(r, transaction)
    
    def __AddTransactionToAllAncestors__(self, root: Transaction, transaction: Transaction):
        if root.Id == transaction.Id:
            print("Transaction already in DAG")
            return

        if root.Id in transaction.ParentIds:
            root.AddChild(transaction)
            transaction.AddParent(root)
        elif root.Children:
            for c in root.Children:
                self.__AddTransactionToAllAncestors__(c, transaction)
        elif root.Id in [r.Id for r in self.Roots]: # if queried node is root
            self.Roots.append(transaction)

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