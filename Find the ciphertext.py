from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import sys

def findCiphertext():
    
    message_A = b"I'll give you 500 and that's my last offer."
    message_B = b"I'll give you 100 and that's my last offer."
    ciphertext_A = b"\xef@\x92<$J\xb2\x8c\xbc\xabl'\x016\xd2{W-8\xcas\x83*\xa1\xef)\xc0\xda\x7fe\xab\xb1\x94\x7fJ\x98\xc8\xeei|'t\xb4"

    key = bytes([a ^ b for a, b in zip(message_A, ciphertext_A)])
    ciphertext_B = bytes([a ^ b for a, b  in zip(message_B, key)])

    return bin(int.from_bytes(ciphertext_B))

print(findCiphertext())