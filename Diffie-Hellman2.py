from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import sys
import math

def myPKCS7(data, block_size):
    k = math.ceil(float(block_size)-(len(data)%float(block_size)))
    if k == 0:
        data += bytes([block_size]) * block_size
    else:   
        data += bytes([k]) * k
    return (data)


def DHandEncrypt(A_Private_Key, B_Private_Key):

    A_des = load_pem_private_key(A_Private_Key, None)
    B_des = load_pem_private_key(B_Private_Key, None)
    shared_key = A_des.exchange(B_des.public_key())
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data'
    ).derive(shared_key)

    return(derived_key)

if __name__ == "__main__":
    A_Private_Key = b'-----BEGIN PRIVATE KEY-----\nMIGcAgEAMFMGCSqGSIb3DQEDATBGAkEAlry2DwPC+pK/0QiOicVAtt6ANsfjmD9P\nQrDC6ZkYcrRf0q0RVzMDTnHWk1mRLVvb6av4HOSkIsk1mMogBcqV0wIBAgRCAkBm\nZK4qUqvU6WaPy4fNG9oWIXchxzztxmA7p9BFXbMzn3rHcW84SDwTWXAjkRd35XPV\n/9RAl06sv191BNFFPyg0\n-----END PRIVATE KEY-----\n' 
    B_Private_Key = b'-----BEGIN PRIVATE KEY-----\nMIGcAgEAMFMGCSqGSIb3DQEDATBGAkEAlry2DwPC+pK/0QiOicVAtt6ANsfjmD9P\nQrDC6ZkYcrRf0q0RVzMDTnHWk1mRLVvb6av4HOSkIsk1mMogBcqV0wIBAgRCAkBn\n9zn/q8GMs7SJjZ+VLlPG89bB83Cn1kDRmGEdUQF3OSZWIdMAVJb1/xaR4NAhlRya\n7jZHBW5DlUF5rrmecN4A\n-----END PRIVATE KEY-----\n'
    plaintext = b"Encrypt me with the derived key!"

    d_key = DHandEncrypt(A_Private_Key, B_Private_Key)
    
    s_o_k = sys.getsizeof(d_key)
    s_o_p = sys.getsizeof(plaintext)

    if(s_o_k != s_o_p):
        plaintext_pd = myPKCS7(plaintext, d_key)
        ciphertext = bytes([x ^ y for x, y in zip(plaintext_pd, d_key)])
    else:
        ciphertext = bytes([x ^ y for x, y in zip(plaintext, d_key)])

    print(ciphertext)



"""
We load the private keys and from the B key we generate the public key in order to obtain the shared key. After that, we generate
we use the given configuration and generate the derived key using the shared key. In the main we XOR the plaintext with the derived key

"""
