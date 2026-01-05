from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate Key Pair
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Private Key
private_pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Public Key
public_pem = key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with open("server_private.pem", "wb") as f:
    f.write(private_pem)

with open("server_public.pem", "wb") as f:
    f.write(public_pem)

print("Keys generated: server_private.pem, server_public.pem")
