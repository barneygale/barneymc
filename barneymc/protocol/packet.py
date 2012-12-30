from time import gmtime, strftime

from data_types import *
from packet_structs import *
import packet_extensions

class Packet:
    def __init__(self, **kargs):
        self.ident     = kargs.get('ident', 0)
        self.direction = kargs.get('direction', CLIENT_TO_SERVER)
        self.data      = kargs.get('data', {})

    def clone(self):
        return Packet(ident = self.ident, direction = self.direction, data = dict(self.data))

    def decode(self, bbuff):
        #Ident
        self.ident = unpack(bbuff, 'ubyte')
        
        #print "###", self.ident
        
        #Payload
        for data_type, name in structs[self.ident][self.direction]:
            self.data[name] = unpack(bbuff, data_type)
        
        #Extension
        if self.ident in packet_extensions.extensions:
            packet_extensions.extensions[self.ident].decode_extra(self, bbuff)

    
    def encode(self):
        #Ident
        output = pack('ubyte', self.ident)
        
        #Extension
        if self.ident in packet_extensions.extensions:
            append = packet_extensions.extensions[self.ident].encode_extra(self)
        else:
            append = ''
        
        #Payload
        for data_type, name in structs[self.ident][self.direction]:
            output += pack(data_type, self.data[name])
        
        return output + append

    def __repr__(self):
        if self.direction == TO_SERVER: s = ">>>"
        else:                           s = "<<<"
        format = "[%s] %s 0x%02x: %-"+str(max([len(i) for i in names.values()])+1)+"s%s"
        return format % (strftime("%H:%M:%S", gmtime()), s, self.ident, names[self.ident], str(self.data))

def read_packet(bbuff, direction):
    p = Packet(direction=direction)
    p.decode(bbuff)
    return p
