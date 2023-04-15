import random
import string

from models.transaction.account import Account
from models.transaction.amount import Amount

MIN_AMOUNT_ACCOUNT_CREATION = 1000
MAX_AMOUNT_ACCOUNT_CREATION = 10000
ACCOUNT_NUM_LENGTH = 20
NUM_OF_ACCOUNTS = 10

def GetRandomAmount(min, max):
    return Amount(random.uniform(min, max))

def GetRandomString(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def GetRandomAccount():
    return Account(GetRandomString(ACCOUNT_NUM_LENGTH), GetRandomAmount(MIN_AMOUNT_ACCOUNT_CREATION, MAX_AMOUNT_ACCOUNT_CREATION))