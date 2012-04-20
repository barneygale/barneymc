import sys
import socket

from protocol.packet import *

def get_info(host, port):
    #Set up our socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    #Send 0xFE: Server list ping
    ping = Packet(ident = 0xFE, direction = TO_SERVER)
    s.send(ping.encode())

    #Receive a response
    response = Packet(direction = FROM_SERVER)
    response.decode(s)
    
    #Close the socket
    s.close()

    assert response.ident == 0xFF
    
    #Split into list
    d = response.data['reason'].split(u'\xa7')

    #Return a dict of values
    return {'motd':            d[0],
            'players':     int(d[1]),
            'max_players': int(d[2])}

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 2:
        print get_info(args[0], int(args[1]))
    else:
        print "Usage: python ping_server.py host port"
