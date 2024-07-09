import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def AES_CTR_FIXED(key, nonce, data):
    b_key = bytes.fromhex(key)
    b_nonce = bytes.fromhex(nonce)
    cipher = Cipher(algorithms.AES(b_key), modes.CTR(b_nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return (ciphertext)

if __name__ == "__main__":

    key = os.urandom(32)
    key = key.hex()
    nonce = os.urandom(16)
    nonce = nonce.hex()
    data = b"Hello, world!"
    print (AES_CTR_FIXED(key, nonce, data))

    

"""
We convert the input to bytes and after that, using the CTR mode, we generate a cipher object of AES, with the given key and nonce.
We obtain the ciphertext by updating the encryptor with the data from input.

"""