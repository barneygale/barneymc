import re

import asyncore
from barneymc.protocol.packet import *
from barneymc.net import proxy

class SimpleTunnel(proxy.ClientHandler):
    def __init__(self, *args, **custom_settings):
        proxy.ClientHandler.__init__(self, *args, **custom_settings)
        
        #Connect to the server
        self.server_handler.connect2()
        
        #Packet handlers
        self.handlers = {
            0x01: self.login,
            0x02: self.handshake
        }
    
    #Just an example...
    def handshake(self, p):
        self.print_packet(p)
        if p.direction == CLIENT_TO_SERVER:
            m = re.match('^([A-Za-z0-9_]{1,16});(.*):(\d+)$', p.data['username_host'])
            if m:
                print "Username: %s" % m.group(1)
                print "Host: %s" % m.group(2)
                print "Port: %d" % int(m.group(3))
        return True #Return true to pass it on to relay this packet (rather than consuming it)
    
    def login(self, p):
        self.print_packet(p)
        if p.direction == SERVER_TO_CLIENT:
            print "Starting pass through..."
            self.start_pass_through()
        return True
    
    def default_handler(self, p):
        self.print_packet(p)
        return True

if __name__ == '__main__':
    p = proxy.Proxy(server_host = 'c.nerd.nu', server_port = 25565, player_handler = SimpleTunnel)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        p.close()
