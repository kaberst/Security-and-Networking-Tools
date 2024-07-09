
def avalanche_calculator(string1, string2):
    import hashlib

    hex_value_string1 = hashlib.sha256(string1.encode()).hexdigest()
    l1 = len(hex_value_string1) * 4
    bin_value_string1 = bin(int(hex_value_string1, 16))
    pval1 = bin_value_string1[2:].zfill(l1-1)

    hex_value_string2 = hashlib.sha256(string2.encode()).hexdigest()
    l2 = len(hex_value_string2)
    bin_value_string2 = bin(int(hex_value_string2, 16))
    pval2 = bin_value_string2[2:].zfill(l2-1)

    xor = int(pval1,2) ^ int(pval2,2)
    xor = bin(xor)[2:].zfill(8)

    k = 0

    for i in range(len(xor)):
        if xor[i] == "1":
            k+=1

    return k


if __name__ == "__main__":
    s1 = input("String 1: ")
    s2 = input("String 2: ")
    print(avalanche_calculator(s1,s2))
