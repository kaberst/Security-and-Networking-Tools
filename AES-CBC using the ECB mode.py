from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

def AESCBC_ECB_decrypt(key, nonce, cipher_data):
    padder = padding.PKCS7(256).padder()
    b_key = bytes.fromhex(key)
    b_nonce = bytes.fromhex(nonce)
    b_cipher_data = bytes.fromhex(cipher_data)
    padded_data = padder.update(b_cipher_data) + padder.finalize()
    cipher = Cipher(algorithms.AES(b_key), modes.ECB())
    decryptor = cipher.decryptor()
    dt = decryptor.update(padded_data) + decryptor.finalize()
    return dt

if __name__ == "__main__":

    key = os.urandom(32)
    h_key = key.hex()
    nonce = os.urandom(16)
    h_nonce = nonce.hex()
    data = b"Hello World!"
    data = data.hex()
    print(AESCBC_ECB_decrypt(h_key, h_nonce, data))
    


"""
After converting everything in bytes, we are padding the data with PKCS7 the same size as the key, 256 bits.
After padding, we use the ECB mode and the key to generate an AES object which is used to decrypt the padded data .

"""