from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, load_pem_parameters, load_pem_public_key, load_pem_private_key
#from dhCheck import dhCheckCorrectness  

def Diffie_Hellman():

    encoded_param = b'-----BEGIN DH PARAMETERS-----\nMEYCQQDP+dSNnBRy4jbHTvr0YcEk0bMzisMy+p/k9VYCb+gPNU/OSDkmEX62YKTc\nj1QrAo8+f3du/bjdfVKfv71LWtxjAgEC\n-----END DH PARAMETERS-----\n'
    given_public_key = b'-----BEGIN PUBLIC KEY-----\nMIGaMFMGCSqGSIb3DQEDATBGAkEAz/nUjZwUcuI2x0769GHBJNGzM4rDMvqf5PVW\nAm/oDzVPzkg5JhF+tmCk3I9UKwKPPn93bv243X1Sn7+9S1rcYwIBAgNDAAJAYyRw\n2K7KvbqudRx9DQtKH/tAQjDtDMIw7hFWYslMFnE/t44wArXQ/wuo0NPhFL4b63R8\nJZA7cF7tP+CAj3WHFA==\n-----END PUBLIC KEY-----\n'
    
    param = load_pem_parameters(encoded_param)
    private_key = param.generate_private_key()
    given_public_key = load_pem_public_key(given_public_key, backend= None)
    shared_key = private_key.exchange(given_public_key)
    public_key = private_key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
    derived_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'handshake data').derive(shared_key)
    
    return public_key, derived_key
    
publicKeySTD, derivedKeySTD = Diffie_Hellman()
print(publicKeySTD,"\n", derivedKeySTD)