import asyncore

from barneymc.protocol.packet import *
from barneymc.protocol import bound_buffer
from barneymc.net import server

#For more complicated usage you'll need to extend server.Server too

class SimpleServer(server.Server):
    def __init__(self, **custom_settings):
        server.Server.__init__(self, **custom_settings)
        self.settings['player_handler'] = SimplePlayerHandler
        self.settings['debug_in'] = True
        self.settings['debug_out'] = True
        
        self.players = []

class SimplePlayerHandler(server.PlayerHandler):
    def __init__(self, rserver, socket, **custom_settings):
        server.PlayerHandler.__init__(self, rserver, socket, **custom_settings)
        
        self.server.players.append(self)
        self.handlers = {
            0xfe: self.server_list_ping}
    
    def server_list_ping(self, packet):
        response = Packet(ident=0xFF, data={
            'reason': u'\xa7'.join((
                self.server.settings['motd'], 
                str(len(self.server.players)-1), 
                str(self.server.settings['max_players'])))})
            
        self.send_packet(response)

    def default_handler(self, packet):
        response = Packet(ident=0xFF, data={'reason': 'Not implemented!'})
        self.send_packet(response)
    
    def handle_close(self):
        self.server.players.remove(self)
        self.close()

if __name__ == '__main__':
    client = SimpleServer(host='localhost', motd='A Minecraft Server')
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        client.close()
