import math
def myPKCS7(data, block_size):
    k = math.ceil(float(block_size)-(len(data)%float(block_size)))
    if k == 0:
        data += bytes([block_size]) * block_size
    else:   
        data += bytes([k]) * k
    return (data)

if __name__ == "__main__":
    data = b"abcd"
    block_size = 16
    print(myPKCS7(data, block_size))
    


"""
Using the formula described in RFC for padding PCKS7, we round up the result of the formula. This
After, if the number of blocks is different from 0, we add k bytes of value k after the data, therefore the new data block will 
be the same size as the input block_size

"""