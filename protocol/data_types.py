import struct
import nbt

data_types = {
	"ubyte":  ('B', 1),
	"byte":   ('b', 1),
	"bool":   ('?', 1),
	"short":  ('h', 2),
	"float":  ('f', 4),
	"int":	  ('i', 4),
	"uint":   ('I', 4),
	"double": ('d', 8),
	"long":   ('q', 8)
}

enchantable = [
		0x103, #Flint and steel
		0x105, #Bow
		0x15A, #Fishing rod
		0x167, #Shears

		#TOOLS
		#sword, shovel, pickaxe, axe, hoe
		0x10C, 0x10D, 0x10E, 0x10F, 0x122, #WOOD
		0x110, 0x111, 0x112, 0x113, 0x123, #STONE
		0x10B, 0x100, 0x101, 0x102, 0x124, #IRON
		0x114, 0x115, 0x116, 0x117, 0x125, #DIAMOND
		0x11B, 0x11C, 0x11D, 0x11E, 0x126, #GOLD

		#ARMOUR
		#helmet, chestplate, leggings, boots
		0x12A, 0x12B, 0x12C, 0x12D, #LEATHER
		0x12E, 0x12F, 0x130, 0x131, #CHAIN
		0x132, 0x133, 0x134, 0x135, #IRON
		0x136, 0x137, 0x138, 0x139, #DIAMOND
		0x13A, 0x13B, 0x13C, 0x13D  #GOLD
]

def pack(data_type, data):
	if data_type in data_types:
		format = data_types[data_type]
		return pack_real(format[0], data)
	
	if data_type == "string8": return pack("short", len(data)) + data
	if data_type == "string16": return pack("short", len(data)) + data.encode('utf-16be')
	if data_type == "slot":
		o = pack('short', data['id'])
		if data['id'] > 0:
			o += pack('byte',  data['amount'])
			o += pack('short', data['damage'])
			if data['id'] in self.enchantable:
				if 'enchantment_data' in data:

					o += pack('short', len(data['enchantment_data']))
					o += data['enchantment_data']

				elif 'enchantments' in data:
					ench = nbt.encode(data['enchantments'])
					ench = nbt.compress(ench)
					o += pack('short', len(ench))
					o += ench
				else:
					o += pack('short', -1)
				
		return o
	if data_type == "metadata":
		o = ''
		for key, tmp in data:
			ty, val = tmp
			x = key | (ty << 5)
			o += pack('ubyte', x)

			if ty == 0: o += pack('byte', val) 
			if ty == 1: o += pack('short', val) 
			if ty == 2: o += pack('int', val) 
			if ty == 3: o += pack('float', val) 
			if ty == 4: o += pack('string16', val)
			if ty == 5:
				o += pack('short', val['id'])
				o += pack('byte',  val['count'])
				o += pack('short', val['damage'])
			if ty == 6:
				for i in range(3):
					o += pack('int', val[i])
		o += pack('byte', 127)
		return o


def unpack(bbuff, data_type):
	if data_type in data_types:
		format = data_types[data_type]
		return unpack_real(bbuff, format[0], format[1])
	
	if data_type == "string8":
		length = unpack(bbuff, 'short')
		return bbuff.recv(length)
	if data_type == "string16":
		length = unpack(bbuff, 'short')
		return bbuff.recv(2*length).decode('utf-16be')
	if data_type == "slot":
		o = {}
		o["id"] = unpack(bbuff, 'short')
		if o["id"] > 0:
			o["amount"] = unpack(bbuff, 'byte')
			o["damage"] = unpack(bbuff, 'short')
			if o['id'] in packet_definitions.enchantable:
				length = unpack(bbuff, 'short')
				if length > 0:
					ench = bbuff.recv(length)
					try: 
						ench = nbt.decompress(ench)
						ench = nbt.decode(StringIO.StringIO(ench))
						o["enchantments"] = ench
					except:
						o["enchantment_data"] = ench
		return o
	if data_type == "metadata":
		metadata = []
		x = unpack(bbuff, 'ubyte')
		while x != 127:
			key = x & 0x1F # Lower 5 bits
			ty  = x >> 5   # Upper 3 bits
			if ty == 0: val = unpack(bbuff, 'byte') 
			if ty == 1: val = unpack(bbuff, 'short') 
			if ty == 2: val = unpack(bbuff, 'int') 
			if ty == 3: val = unpack(bbuff, 'float') 
			if ty == 4: val = unpack(bbuff, 'string16')
			if ty == 5:
				val = {}
				val["id"]	 = unpack(bbuff, 'short')
				val["count"]  = unpack(bbuff, 'byte')
				val["damage"] = unpack(bbuff, 'short')
			if ty == 6:
				val = []
				for i in range(3):
					val.append(unpack(bbuff, 'int'))
			metadata.append((key, (ty, val)))
			x = unpack(bbuff, 'byte')
		return metadata
				
def unpack_real(bbuff, data_type, length):
	return struct.unpack_from('!'+data_type, bbuff.recv(length))[0]

def pack_real(data_type, data):
	return struct.pack('!'+data_type, data)

def unpack_array(bbuff, data_type, count):
	a = []
	for i in range(count):
		a.append(unpack(bbuff, data_type))
	return a

def pack_array(data_type, data):
	o = ''
	for d in data:
		o += pack(data_type, d)
	return o

def unpack_array_fast(bbuff, data_type, count):
	data_type = data_types[data_type]
	length = data_type[1] * count
	format = data_type[0] * count
	return struct.unpack_from(format, bbuff.recv(length))
	
def pack_array_fast(data_type, data):
	data_type = data_types[data_type]
	return struct.pack(data_type[0]*len(data), *data)
