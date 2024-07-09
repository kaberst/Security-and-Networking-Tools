import string 

def encrypt_affine(plain_text, a, b):
    cipher_text = ""
    plain_to_cipher = {}
    A = string.ascii_uppercase

    for i in range(len(string.ascii_uppercase)):
        plain_to_cipher[string.ascii_uppercase[i]] = i
    
    for i in plain_text:
        if i in plain_to_cipher.keys():
            cipher_text += A[(a * plain_to_cipher.get(i) +b)%26]
        else:
            cipher_text += i
   
    return(cipher_text)


def main():
    plaintext = input("Plaintext: ")
    a = int(input("Key 1: "))
    b = int(input("Key 2: "))
    print(encrypt_affine(plaintext, a, b))

if __name__ == "__main__":
    main()