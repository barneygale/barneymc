import asyncore

from barneymc.protocol.packet import *
from barneymc.protocol import bound_buffer
from barneymc.net import server
from barneymc.net import encryption
import random

#For more complicated usage you'll need to extend server.Server too

class SimpleServer(server.Server):
    def __init__(self, **custom_settings):
        server.Server.__init__(self, **custom_settings)
        self.settings['player_handler'] = SimplePlayerHandler
        self.settings['debug_in'] = True
        #self.settings['debug_out'] = True
        
        self.players = []

class SimplePlayerHandler(server.PlayerHandler):
    def __init__(self, rserver, socket, **custom_settings):
        server.PlayerHandler.__init__(self, rserver, socket, **custom_settings)
        
        self.server.players.append(self)
        self.handlers = {
            0x00: self.reflect,
            0x01: self.login,
            0x02: self.handshake,
            0xfc: self.encryption_response,
            0xfe: self.server_list_ping}
        
    
    def login(self, packet):
        print "<-- login"
        print "--> login"
        self.send_packet(Packet(ident=0x01, data={
            'entity_id': 1, 
            'level_type': u'default', 
            'game_mode': 0, 
            'dimension': 0, 
            'difficulty': 1, 
            'not_used': 0, 
            'max_players': 20
        }))
    def handshake(self, packet):
        print "<-- handshake"
        print "--> encryption request"
        response = Packet(ident=0xfd, data = {
            'server_id': '%x' % random.randint(0, pow(2, 8*8)-1),
            'server_public_key': self.server.encoded_public_key})
        
        self.send_packet(response)
    
    def encryption_response(self, packet):
        print "<-- encryption response"
        print "--> encryption response"
        self.send_packet(Packet(ident=0xfc, data={'encrypted_shared_secret': []}))
        
        data = packet.data['encrypted_shared_secret']
        data = ''.join([chr(i) for i in data])
        data = encryption.decrypt_shared_secret(self.server.key_pair, data)
        
        self.stream_cipher.shared_secret = data
        self.stream_cipher.start_encrypting()
        print '### protocol encryption enabled'
    
    def server_list_ping(self, packet):
        response = Packet(ident=0xFF, data={
            'reason': u'\xa7'.join((
                self.server.settings['motd'], 
                str(len(self.server.players)-1), 
                str(self.server.settings['max_players'])))})
            
        self.send_packet(response)

    def default_handler(self, packet):
        #response = Packet(ident=0xFF, data={'reason': 'Not implemented!'})
        #self.send_packet(response)
        pass
    
    def handle_close(self):
        self.server.players.remove(self)
        self.close()

if __name__ == '__main__':
    client = SimpleServer(host='localhost', motd='A Minecraft Server')
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        client.close()
