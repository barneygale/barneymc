class BufferUnderflowException(Exception):
	pass

class BoundBuffer:
	backup = ''
	def __init__(self, *args):
		self.buff = (args[0] if args else '')
	
	def read(self, bytes):
		if len(self.buff) < bytes:
			raise BufferUnderflowException()
		o, self.buff = self.buff[:bytes], self.buff[bytes:]
		return o

	def save(self):
		self.backup = self.buff
	
	def revert(self):
		self.buff = self.backup
	
	recv = read
