import asyncore

from protocol import bound_buffer
from net import server
from protocol.packet import *

class SimplePlayerHandler(server.PlayerHandler):
	def __init__(self, rserver, socket, **custom_settings):
		server.PlayerHandler.__init__(self, rserver, socket, **custom_settings)

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

if __name__ == '__main__':
	client = server.Server(player_handler=SimplePlayerHandler, host='localhost', debug_out = True, debug_in = True)
	try:
		asyncore.loop()
	except KeyboardInterrupt:
		client.close()
