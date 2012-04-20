import socket
import asynchat

from protocol import bound_buffer
from protocol.packet import *


class Client(asynchat.async_chat):
    node = NODE_CLIENT
    settings = {
        'host': 'localhost',
        'port': 25565,
        'debug_in': False,
        'debug_out': False}

    rbuff = bound_buffer.BoundBuffer()
    handlers = {}

    def __init__(self, **custom_settings):
        self.settings.update(custom_settings)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.settings['host'], self.settings['port']))
        
        asynchat.async_chat.__init__(self, sock = s)
        self.set_terminator(None)

    def send_packet(self, packet):
        packet.direction = self.node
        if self.settings['debug_out']:
            print packet
        data = packet.encode()
        self.push(data)

    def collect_incoming_data(self, data):
        if len(data) > 0:
            self.rbuff.buff += data
            while True:
                try:
                    self.rbuff.save()
                    p = read_packet(self.rbuff, other_node[self.node])
                    if self.settings['debug_in']:
                        print p
                    
                    self.handlers.get(p.ident, self.default_handler)(p)
            
                except bound_buffer.BufferUnderflowException:
                    self.rbuff.revert()
                    return
    
    def found_terminator(self):
        pass

    def default_handler(self, packet):
        pass
    
    def reflect(self, packet):
        self.send_packet(packet.clone())
        
    def print_packet(self, packet):
        print packet
