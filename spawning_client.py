import asyncore
import sys

from barneymc.protocol.packet import *
from barneymc.protocol import bound_buffer
from barneymc.net import client
from barneymc.net import encryption

class SpawningClient(client.Client):
    spawned = False
    def __init__(self, **settings):
        self.handlers = {
            0x00: self.reflect,
            0x01: self.login,
            0x02: self.handshake,
            0x0d: self.position_and_look,
            0xfc: self.encrypt_res,
            0xfd: self.encrypt_req,
            0xff: self.disconnect}
        
        if 'password' in settings:
            
        client.Client.__init__(self, **settings)
        self.connect2()
        
        self.send_packet(Packet(ident=0x02, data={'protocol_version': 32, 'username': self.settings['username'], 'host': self.settings['host'], 'port': self.settings['port']}))
        print "--> handshake"

    def login(self, packet):
        print "<-- login"
        print packet

    def handshake(self, packet):
        pass

    def encrypt_res(self, packet):
        print "<-- encryption response"
        print '### protocol encryption enabled'
        self.stream_cipher.start_encrypting()
        self.send_packet(Packet(ident=0x01))
        print "--> login"

    def encrypt_req(self, packet):
        print "<-- encryption request"
        d = packet.data['server_public_key']
        d = ''.join([chr(i) for i in d])
        
        #http://session.minecraft.net/game/joinserver.jsp?user=username&sessionId=user_session&serverId=hash
        self.key_pair = encryption.import_public_key(d)
        self.stream_cipher.generate_shared_secret()
        
        d = encryption.encrypt_shared_secret(self.key_pair, self.stream_cipher.shared_secret)
        
        self.send_packet(Packet(ident=0xFC, data={'encrypted_shared_secret': [ord(c) for c in d]}))
        print "--> encryption response"
        
        #self.encryption.load_public_key(packet.data['server_public_key'])
        #self.print_packet(packet)
    
    #def encrypt_res(self, packet):
    #    self.print_packet(packet)
    
    def position_and_look(self, packet):
        #self.print_packet(packet)
        if not self.spawned:
            self.reflect(packet)
            self.spawned = True
            print '### spawned!'
        else:
            raise Exception("Server corrected our position - disconnecting!")
        
    def disconnect(self, packet):
        self.close()
    
                
if __name__ == '__main__':
    if len(sys.argv) in (4, 5):
        print "Usage: python spawning_client.py host port username [password]"
        sys.exit(1)
    args = dict(zip(('host', 'port', 'username'), sys.argv[1:4]))
    args['port'] = int(args['port'])
    if len(sys.argv) == 5:
        args['password'] = sys.argv[4]
    client = SpawningClient(**args)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        client.close()

