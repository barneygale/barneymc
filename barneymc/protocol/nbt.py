import struct
import collections
from StringIO import StringIO
import gzip

endian = '>'

def unpack(buff, format):
    return struct.unpack_from(endian+format, buff.read(struct.calcsize(format)))[0]
def pack(value, format):
    return struct.pack(endian+format, value)

class TAG:
    def __init__(self, ty, *args):
        self.type = ty
        if args:
            self.name = args[0]
        else: self.name = ''
    def __getattr__(self, name):
        return getattr(self.value, name)
    def __getitem__(self, name):
        return self.value[name]
    def decode(self, buff):
        self.value = unpack(buff, self.struct)
    def encode(self):
        return pack(self.value, self.struct)
    def normalized(self):
        return self.value
        
class TAG_Byte(TAG):
    struct = 'b'
class TAG_Short(TAG):
    struct = 'h'
class TAG_Int(TAG):
    struct = 'i'
class TAG_Long(TAG):
    struct = 'q'
class TAG_Float(TAG):
    struct = 'f'
class TAG_Double(TAG):
    struct = 'd'
class TAG_Byte_Array(TAG):
    def decode(self, buff):
        l = unpack(buff, 'i')
        self.value = [unpack(buff, 'b') for i in range(l)]
    def encode(self):
        o = pack(len(self.value), 'i')
        o += ''.join([pack(i, 'b') for i in self.value])
        return o
class TAG_String(TAG):
    def decode(self, buff):
        l = unpack(buff, 'h')
        self.value = buff.read(l)
    def encode(self):
        return pack(len(self.value), 'h') + self.value
class TAG_List(TAG):
    def decode(self, buff):
        self.child_tag = unpack(buff, 'b')
        l = unpack(buff, 'i')
        self.value = []
        for i in range(l):
            child = handlers[self.child_tag](self.child_tag)
            child.decode(buff)
            self.value.append(child)
    def encode(self):
        o = pack(self.child_tag, 'b')
        o+= pack(len(self.value), 'i')
        o+= ''.join([i.encode() for i in self.value])
        return o
    def normalized(self):
        return [i.normalized() for i in self.value]
class TAG_Compound(TAG):
    def decode(self, buff):
        self.value = collections.OrderedDict()
        child_tag = buff.read(1)
        while child_tag != '' and child_tag != '\x00':
            child_tag = ord(child_tag)
            name_len = unpack(buff, 'h')
            name = buff.read(name_len)
            child = handlers[child_tag](child_tag, name)
            child.decode(buff)
            self.value[name] = child
            child_tag = buff.read(1)
    def encode(self):
        o = ''
        for name, child in self.value.items():
            o += pack(child.type, 'b') #Type
            o += pack(len(name), 'h')  #Name length
            o += name                  #Name
            o += child.encode()        #Payload
        return o + '\x00'
    def normalized(self):
        return dict([(name, child.normalized()) for name, child in self.value.items()])

handlers = {
    1: TAG_Byte,
    2: TAG_Short,
    3: TAG_Int,
    4: TAG_Long,
    5: TAG_Float,
    6: TAG_Double,
    7: TAG_Byte_Array,
    8: TAG_String,
    9: TAG_List,
    10: TAG_Compound}

def decode(buff):
    t = TAG_Compound(10)
    t.decode(buff)
    return list(t.value.values())[0]

def encode(obj):
    t = TAG_Compound(10)
    t.value = {'': obj}
    return t.encode()[:-1]

def compress(s):
    io = StringIO()
    f = gzip.GzipFile(fileobj=io, mode='w')
    f.write(s)
    f.close()
    return io.getvalue()

def decompress(s):
    f = gzip.GzipFile(fileobj=StringIO(s))
    o = f.read()
    f.close()
    return o
