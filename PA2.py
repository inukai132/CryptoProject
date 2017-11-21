#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is the hardcoded version of the paddingOracle.py.
# Instead of sending the packet to a server, it sends it to a method that mimics the server.
# I'm including this to help with testing
import json, base64
import requests
from Crypto.Cipher import AES

# Constants
url = "http://localhost:8080/decrypt"
my_key = "1010101010101010"
BLOCK_SIZE = 16
INIT_VEC = "SameIVisn'tgood."
EXAMPLE_TEXT = "zZIzoCIZw6wELA9KEu5k/YIshXB1u6K+o32TnIIaiKXKWCY06twVdlfnVaIJqLwtT9zZsk1L+Z/jQu50uz6cB12tsQQNczzqWHLkhlXnCPQbRJszr7LDw9EuuHkV+Pbf7pouSLml7jt2wZliHCdv8trjG+EOU0FgLPHNLDfQKIIW6KIBIcQ0VFX94QYwY0FsFj6CKz4TlCyeCx/LhPW6cg=="


def numberify(characters):
    return map(lambda x: ord(x), characters)

def stringify(numbers):
    return "".join(map(lambda x: chr(x), numbers))

class ValueError(Exception):
    pass

def pad(s):
    padByte = 16-len(s) % 16
    return s + chr(padByte)*padByte

def unpad(s):
    padByte = ord(s[-1])
    if padByte == 0 or padByte > 16:
        raise ValueError("Incorrect Padding Byte, greater than 16")
    for i in range(padByte):
        if ord(s[-(i+1)]) != padByte:
            raise ValueError("Incorrect Padding Byte, found data in the padding")
    return s[:-padByte]

def serverDecrypt(data, key, iv):
    cipher = base64.b64decode(data)
    crypter = AES.new(key, AES.MODE_CBC, iv)
    intermediate = crypter.decrypt(cipher)
    plain = unpad(intermediate)
    #print numberify(plain)
    #print numberify(intermediate)
    #return crypter.decrypt(cipher)
    return plain

def blockify(text, block_size=BLOCK_SIZE):
    return [text[i:i+block_size] for i in range(0, len(text), block_size)]

def doPost(url, key, data):
    payload = {'key':key, 'data':data}
    response = requests.post(url, data = payload, proxies=proxies)
    return response

if __name__ == "__main__":

    #Global Variables
    EXAMPLE_TEXT = base64.b64decode(EXAMPLE_TEXT)
    ciphertext = numberify(EXAMPLE_TEXT)
    blocks = blockify(ciphertext)
    blockCount = len(blocks)

    cleartext = []
    for block_num in range(blockCount-1, -1, -1):
        print "cracking block {} out of {}".format(block_num+1, blockCount)
        i2 = [0] * 16
        p2 = [0] * 16
        c2 = blocks[block_num]
        c1 = blocks[block_num-1]
        if block_num == 0:
            c1 = numberify(list(INIT_VEC))
        for i in xrange(15,-1,-1):
            for b in xrange(0,256):
                #print "i = {}, b = {}".format(i, b)
                prefix = c1[:i]
                pad_byte = (BLOCK_SIZE-i)
                suffix = [pad_byte ^ val for val in i2[i+1:]]
                #print suffix
                evil_c1 = prefix + [b] + suffix
                #print pad_byte
                #print evil_c1
                data = base64.b64encode(stringify(evil_c1 + c2))
                try:
                    x = serverDecrypt(data, my_key, INIT_VEC)
                except ValueError:
                    pass
                else:
                    #print numberify(x)
                    #print evil_c1 + c2
                    x = pad(x)
                    y = numberify(x[i+16])
                    evil_p2 = int(''.join(str(digit) for digit in y))
                    #print evil_p2
                    i2[i] = evil_c1[i] ^ evil_p2
                    p2[i] = c1[i] ^ i2[i]
                    break
        #print i2
        #print evil_c1
        #print suffix
        cleartext = p2+cleartext
    print "========================="
    print stringify(cleartext)
    print "========================="
