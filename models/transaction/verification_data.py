

import enum


class ConsensusResult(enum.Enum):
    ACCEPTED = 0
    REJECTED_FOR_ANOTHER = 1
    NONE_ACCEPTED = 2

class VerificationData:
    def __init__(self) -> None:
        self.Chit = False
        self.Confidence = 0
        self.ConsecutiveSuccesses = 0
        self.Validated = False