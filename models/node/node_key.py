from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


class NodeKey:
    PUBLIC_EXPONENT = 65537
    KEY_SIZE = 2048
    def __init__(self) -> None:
        self.PrivateKey = rsa.generate_private_key(
            public_exponent=NodeKey.PUBLIC_EXPONENT,
            key_size=NodeKey.KEY_SIZE,
            backend=default_backend()
        )
        self.PublicKey = self.PrivateKey.public_key()