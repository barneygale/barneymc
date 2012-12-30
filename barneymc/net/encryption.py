from barneymc.protocol.packet import *
import base64
import random

import M2Crypto as m2crypto

##
## From https://github.com/bozhu/RC4-Python
##

#Courtesy of sadimusi
class RC4(object):
    def __init__(self, key):
        self.key = key
        x = 0
        self.box = box = range(256)
        for i in range(256):
            x = (x + box[i] + ord(key[i % len(key)])) % 256
            box[i], box[x] = box[x], box[i]
        self.x = self.y = 0

    def crypt(self, data):
        out = ""
        box = self.box
        for char in data:
            self.x = x = (self.x + 1) % 256
            self.y = y = (self.y + box[self.x]) % 256
            box[x], box[y] = box[y], box[x]
            out += chr(ord(char) ^ box[(box[x] + box[y]) % 256])
        return out


class StreamCipher:
    enabled = False
    shared_secret = None

    def __init__(self, **kwargs):
        if 'shared_secret' in kwargs:
            self.shared_secret = kwargs['shared_secret']
    
    def generate_shared_secret(self):
        self.shared_secret = ''.join([chr(random.randint(0,255)) for i in range(16)])
    
    def start_encrypting(self):
        self.generators = {
            CLIENT_TO_SERVER:RC4(self.shared_secret),
            SERVER_TO_CLIENT:RC4(self.shared_secret)
        }
        self.enabled = True
    
    def encrypt(self, data, direction):
        if self.enabled:
            return self.generators[direction].crypt(data)
        else:
            return data

    decrypt = encrypt
    
def generate_key_pair(self):
    return m2crypto.RSA.gen_key(1024, 0x10001, callback=lambda: True)

pem_start = '-----BEGIN PUBLIC KEY-----'
pem_end = '-----END PUBLIC KEY-----'

#Dumps the public key to the format minecraft uses
#(python makes us jump through some hoops)
def export_public_key(key_pair):
    #First extract a PEM file
    bio = m2crypto.BIO.MemoryBuffer('')
    key_pair.save_pub_key_bio(bio)
    d = bio.getvalue()

    #Get just the key data
    s = d.find(pem_start)
    e = d.find(pem_end)
    assert s != -1 and e != -1
    out = d[s+len(pem_start):e]
    
    #Decode
    out = base64.decodestring(out)
    
    return out

#The reverse. string -> new RSA instance
def import_public_key(bytes):
    #base64
    data = base64.encodestring(bytes)
    
    #format
    data = pem_start + '\n' + data + pem_end
    
    #initialise buffer
    bio = m2crypto.BIO.MemoryBuffer(data)
    
    #load
    return m2crypto.RSA.load_pub_key_bio(bio)

def encrypt_shared_secret(keypair, secret):
    return keypair.public_encrypt(secret, m2crypto.m2.pkcs1_padding)

def decrypt_shared_secret(keypair, data):
    return keypair.private_decrypt(data, m2crypto.m2.pkcs1_padding)
