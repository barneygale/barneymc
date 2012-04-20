import socket
import asyncore
import asynchat

import client
from protocol.packet import *

class PlayerHandler(client.Client):
    node = NODE_SERVER
    settings = {
        'debug_in': False,
        'debug_out': False}

    def __init__(self, rserver, socket, **custom_settings):
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
        'interface': '',
        'port': 25565,
        'max_players': 20,
        'motd': 'A Minecraft Server'}
    
    players = []

    def __init__(self, **custom_settings):
        self.settings.update(custom_settings)
        
        asyncore.dispatcher.__init__(self)
        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        
        self.bind((self.settings['interface'], self.settings['port']))
        
        self.listen(self.settings['max_players'])
        
    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            return
        else:
            sock, addr = pair
            handler = self.settings['player_handler'](self, sock, **self.settings)
            self.players.append(handler)
