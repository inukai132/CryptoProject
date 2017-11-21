#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, base64 #for b64 and json display
import requests # for making post requests (this has ran slowly for me, i recommend replacing this)
from Crypto.Cipher import AES # for cbc

# Bug 1: The Jout = Json.dumps line at the end of server.py's /decrypt path is throwing errors
# Bug 2: Requests are unusually slow, at least on my hardware

# TODO: Add code to crack init vector from site
# TODO: Add a way to elegantly insert ciphertext without hard-coding

proxies = { # Disable proxies to speed up requests
  "http": None,
  "https": None,
}

# Constants
BLOCK_SIZE = 16  # bytes
INIT_VEC = "SameIVisn'tgood."  # At the moment this is a constant, this should be something we take in
url = "http://localhost:8080/decrypt" # Our url
my_key = "1010101010101010" # Our key
# Sample text pulled from our home page
EXAMPLE_TEXT = "zZIzoCIZw6wELA9KEu5k/YIshXB1u6K+o32TnIIaiKXKWCY06twVdlfnVaIJqLwtT9zZsk1L+Z/jQu50uz6cB12tsQQNczzqWHLkhlXnCPQbRJszr7LDw9EuuHkV+Pbf7pouSLml7jt2wZliHCdv8trjG+EOU0FgLPHNLDfQKIIW6KIBIcQ0VFX94QYwY0FsFj6CKz4TlCyeCx/LhPW6cg=="

def pad(s): # Pad function
    padByte = 16-len(s) % 16
    return s + chr(padByte)*padByte

def blockify(text, block_size=BLOCK_SIZE): # Block function. Splits text into blocks of size 16.
    return [text[i:i+block_size] for i in range(0, len(text), block_size)]

def numberify(characters): # convert list entries to integers
    return map(lambda x: ord(x), characters)

def stringify(numbers): # convert list entries to strings
    return "".join(map(lambda x: chr(x), numbers))

def doPost(url, key, data):
    payload = {'key':key, 'data':data}
    response = requests.post(url, data = payload, proxies=proxies)
    return response

if __name__ == "__main__":

    #Global Variables
    EXAMPLE_TEXT = base64.b64decode(EXAMPLE_TEXT) # Decode our example text
    ciphertext = numberify(EXAMPLE_TEXT) # Convert to integers
    blocks = blockify(ciphertext) # Convert our integer string to blocks
    blockCount = len(blocks) # Get the number of blocks

    cleartext = [] # Create empty array to store our blocks of plaintext
    for block_num in range(blockCount-1, -1, -1): # let block_num be an iterator for which blocks we're cracking, starting at 15
        print "cracking block {} out of {}".format(block_num+1, blockCount)
        i2 = [0] * 16 # Create empty array for this block's intermediate state
        p2 = [0] * 16 # Create empty array for this block's plaintext
        c2 = blocks[block_num] # C2 is the block we are attempting to crack
        c1 = blocks[block_num-1] # C1 is the block before it, our attack is based on
                                 # manipulating values of C1 to yield the intermediate state
                                 # which we can then use to derive the true plaintext

        if block_num == 0: # If we're on block zero, then we need the IV to decode the block. So replace C1 with the IV
            c1 = numberify(list(INIT_VEC)) # Convert the IV string to a list, convert list to ints

        # Put together our dummy c1
        for i in xrange(15,-1,-1): # For each byte, i, in the 16 byte list, descending from byte 15 to byte 0
            for b in xrange(0,256): # We'll be incrementing byte, b, from 0 to 256 until the oracle tells us we have the right padding
                print "i = {}, b = {}".format(i, b)
                # Our dummy c1, c1_evil, consists of a prefix + iterator byte + suffix
                prefix = c1[:i] # This is just the normal c1 until the iterator byte
                pad_byte = (BLOCK_SIZE-i) # 
                suffix = [pad_byte ^ val for val in i2[i+1:]] # This is the pad_byte XOR the values in our current i2 block 
                evil_c1 = prefix + [b] + suffix # Put it all together
                data = base64.b64encode(stringify(evil_c1 + c2)) # Now we combine our lists, convert them back to a string, and encode them for the website
                
                # Send our data to the server
                x = doPost(url, my_key, data) # This is a post request via import request, it returns a response object, which we store in x
                # Process response
                if x.status_code == 200: # Status code should be 200 on valid padding, otherwise 500 and we pass
                    alpha = (eval(x.text)['data']) #unpack the object
                    x = pad(alpha) # The object is returned unpadded, here we repad so we can get the ith fake plaintext byte
                    y = numberify(x[i+16]) # and here we access it. The plaintext byte corresponding to c2[i] is p2'[i]. We pull from i+16 since the list is p1'+p2', where p' is our fake plaintext
                    evil_p2 = int(''.join(str(digit) for digit in y)) # This lovely bit of code salad is used to pull the single digit list object into an int
                    i2[i] = evil_c1[i] ^ evil_p2 # We derive i2[i]
                    p2[i] = c1[i] ^ i2[i] # We derive p2[i]
                    break
        cleartext = p2 + cleartext # Update cleartext
    print "========================="
    print unpad(stringify(cleartext)) # Display unpadded results
    print "========================="
