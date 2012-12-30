import asyncore

from barneymc.protocol.packet import *
from barneymc.protocol import bound_buffer
from barneymc.net import client

class SimpleClient(client.Client):
    spawned = False
    def __init__(self, **settings):
        self.handlers = {
            0x00: self.reflect, #Echos the packet back to the server
            0x01: self.print_packet, #Prints debug info on the packet
            0x02: self.handshake,
            0x0d: self.positionandlook,
            0xff: self.disconnect}
        
        client.Client.__init__(self, **settings)
        
        self.connect2()

        self.send_packet(Packet(ident=0x02, data={'protocol_version': 32, 'username': self.settings['username'], 'host': self.settings['host'], 'port': self.settings['port'])}))

    def login(self, packet):
        pass        

    def handshake(self, packet):
        self.print_packet(packet)
        
        if packet.data['connection_hash'] != '-':
            print "This example client only supports offline-mode servers"
            self.close()
        else:
            self.send_packet(Packet(ident=0x01, data={
                'username': self.settings['username'], 
                'protocol_version': 29, 
                'not_used_1': '',
                'not_used_2': 0,
                'not_used_3': 0,
                'not_used_4': 0,
                'not_used_5': 0,
                'not_used_6': 0
            }))
        
    def positionandlook(self, packet):
        self.print_packet(packet)
        if not self.spawned:
            self.reflect(packet)
            self.spawned = True
            print 'Spawned!'
        else:
            raise Exception("Server corrected our position - disconnecting!")
        
    def disconnect(self, packet):
        self.close()
    
                
if __name__ == '__main__':
    client = SimpleClient(host='localhost', username='bot', debug_out = True)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        client.close()

