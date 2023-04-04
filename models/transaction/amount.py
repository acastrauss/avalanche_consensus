
class Amount:
    def __init__(self, amount:float) -> None:
        self.Amount = amount
    
    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, self.__class__):
            return __o.Amount == self.Amount
        else:
            return False

    def __gt__(self, am):
        return self.Amount > am.Amount

    def __sub__(self, am):
        return Amount(self.Amount - am.Amount)
    
    def __add__(self, am):
        return Amount(self.Amount + am.Amount)