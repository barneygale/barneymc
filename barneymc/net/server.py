import socket
import asyncore
import asynchat

from barneymc.protocol.packet import *
from barneymc.protocol import bound_buffer
import client
import encryption
import time #todo: remove
import StringIO

import M2Crypto as m2crypto

class PlayerHandler(client.Client):
    node = NODE_SERVER
    settings = {
        'debug_in': False,
        'debug_out': False}

    def __init__(self, rserver, socket, **custom_settings):
        self.rbuff = bound_buffer.BoundBuffer()
        self.stream_cipher = encryption.StreamCipher()
        self.server = rserver
        self.settings.update(custom_settings)
        asynchat.async_chat.__init__(self, sock = socket)
        self.set_terminator(None)

    def handle_close(self):
        self.server.players.remove(self)
        self.close()

class Server(asyncore.dispatcher):
    settings = {
        'player_handler': PlayerHandler,
        'host': '',
        'port': 25565,
        'max_players': 20}

    def __init__(self, **custom_settings):
        self.settings.update(custom_settings)
        
        #Generate keypair
        self.key_pair = m2crypto.RSA.gen_key(1024, 0x10001, callback=lambda: True)
        
        #Export public key to minecraft format
        d = encryption.export_public_key(self.key_pair)
        
        #Convert to byte array
        d = [ord(i) for i in d]
        
        #Save
        self.encoded_public_key = d
        
        asyncore.dispatcher.__init__(self)
        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        
        self.bind((self.settings['host'], self.settings['port']))
        
        self.listen(self.settings['max_players'])
        
    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            return
        else:
            sock, addr = pair
            handler = self.settings['player_handler'](self, sock, **self.settings)
    
