import asyncore
import traceback
import socket
import sys

from barneymc.protocol.packet import *
import server
import client

class ClientHandler(server.PlayerHandler):
    node = NODE_SERVER
    pass_through = False
    pass_through_starting = False
   
    def __init__(self, rserver, socket, **custom_settings):
        server.PlayerHandler.__init__(self, rserver, socket, **custom_settings)
        self.server_handler = ServerHandler(self, host = self.settings['server_host'], port = self.settings['server_port'])

        self.collect_incoming_data_old = self.collect_incoming_data
        self.collect_incoming_data = self.collect_incoming_data_new
        
    def collect_incoming_data_new(self, data):
        if self.pass_through:
            self.server_handler.push(data)
        else:
            if self.pass_through_starting:
                #Flush buffers
                self.push(self.server_handler.rbuff.flush())
                self.server_handler.push(self.rbuff.flush())
                
                self.pass_through = True
                self.pass_through_starting = False
            else:
                self.collect_incoming_data_old(data)
    
    def default_handler(self, packet):
        return True
    
    def dispatch_packet(self, packet):
        transmit = self.handlers.get(packet.ident, self.default_handler)(packet)
        if transmit:
            if packet.direction == TO_CLIENT:
                self.send_packet(packet)
            elif packet.direction == TO_SERVER:
                self.server_handler.send_packet(packet)
    
    def start_pass_through(self):
        if not self.pass_through and not self.pass_through_starting:
            self.stop_packet_loop = True
            self.server_handler.stop_packet_loop = True
            self.pass_through_starting = True
    
    def handle_close(self):
        self.server_handler.close()
        self.close()
    
    def handle_error2(self, err):
        if err == 0:
            info = sys.exc_info()
            if info[0] in (socket.gaierror, socket.error):
                self.log('Can\'t reach server: %s' % info[1][1])
                self.send_packet(Packet(ident=0xff, data={'reason': 'brb'}))
            else:
                self.log("Got a python exception...")
                self.log(traceback.format_exc())
        elif err == 61:
            self.send_packet(Packet(ident=0xff, data={'reason': 'Server unreachable'}))
        else:
            self.send_packet(Packet(ident=0xff, data={'reason': 'Unexpected error'}))

    def handle_error(self):
        return self.handle_error2(self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))

    def log(self, message):
        print '[DEBUG] %s' % (message.encode("ascii", "ignore"))

class ServerHandler(client.Client):
    node = NODE_CLIENT
    def __init__(self, client_handler, **custom_settings):
        client.Client.__init__(self, **custom_settings)
        self.client_handler = client_handler

        self.collect_incoming_data_old = self.collect_incoming_data
        self.collect_incoming_data = self.collect_incoming_data_new
        
    def collect_incoming_data_new(self, data):
        if self.client_handler.pass_through:
            self.client_handler.push(data)
        else:
            self.collect_incoming_data_old(data)

    def dispatch_packet(self, packet):
        #We hand all packets we receive to the ClientHandler's packet handlers
        self.client_handler.dispatch_packet(packet)

    def handle_close(self):
        self.client_handler.close()
        self.close()
    
    def handle_error(self):
        self.client_handler.handle_error2(self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR))

class Proxy(server.Server):
    def __init__(self, **custom_settings):
        server.Server.__init__(self, **custom_settings)
        self.settings['player_handler'] = self.settings.get('player_handler', ClientHandler)
