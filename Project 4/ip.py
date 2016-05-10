#from socket import socket, SOCK_RAW, AF_PACKET
import socket
import sys
from struct import*
from random import randint

class ChecksumError(Exception):
	"""docstring for ChecksumError"""
	def __init__(self, layer=''):
		self.layer = layer
		
	def __str__(self):
		return "Checksum not correct at %s" %(self.layer)

class IPPacket:
	def __init__(self, saddr='', daddr='', data=''):
		self.ip_ver = 4 # ipv4
		self.ip_ihl = 5
		self.ip_tos = 0
		self.ip_total_len = 20
		self.ip_id = 0
		self.ip_flag_df = 1 # do not fragment
		self.ip_flag_mf = 0
		self.ip_frag_off = 0
		self.ip_ttl = 255 
		self.ip_proto = socket.IPPROTO_TCP
		self.ip_check = 0 
		self.ip_saddr = saddr
		self.ip_daddr = daddr
		self.ip_ihl_ver = (self.ip_ver << 4) + self.ip_ihl
		self.ip_flag_frag = (((self.ip_flag_df << 1) + self.ip_flag_mf) << 13) + self.ip_frag_off
		self.data = data

	def carry_around_add(self, s):
		c = (s >> 16) + (s & 0xffff)
		c += c >> 16
		c = ~c& 0xffff
		return c

	def ip_checksum(self, msg): 
		if len(msg) % 2 != 0:
		    msg = msg + pack('B', 0)
		s = 0
		for i in range(0, len(msg), 2):
			w = ord(msg[i]) + (ord(msg[i+1]) << 8)
			s += w
		s = self.carry_around_add(s)
		return s

	def build(self):
		self.ip_id = randint(0, 65535)
		self.ip_total_len = self.ip_ihl * 4 + len(self.data)

		src_addr = socket.inet_aton(self.ip_saddr)
		dest_addr = socket.inet_aton(self.ip_daddr)
		#print "src : %s and dest : %s " %(self.ip_saddr, self.ip_daddr)
		pesudo_ip_header = pack('!BBHHHBBH4s4s', self.ip_ihl_ver, self.ip_tos, self.ip_total_len, self.ip_id, self.ip_flag_frag, 
								self.ip_ttl, self.ip_proto, self.ip_check, src_addr, dest_addr)
		# calculate the checksum
		self.ip_check = self.ip_checksum(pesudo_ip_header)
		#print 'ip checksum : %s' %self.ip_check
		ip_header = pack('!BBHHHBB', self.ip_ihl_ver, self.ip_tos, self.ip_total_len, self.ip_id, self.ip_flag_frag, 
					self.ip_ttl, self.ip_proto) + pack('H', self.ip_check) + pack('!4s4s', src_addr, dest_addr)
		packet = ip_header + self.data
		return packet

	def unbuild(self,rcv_packet):
		[self.ip_ihl_ver, self.ip_tos, self.ip_total_len, self.ip_id, self.ip_flag_frag, \
		self.ip_ttl, self.ip_proto] = unpack('!BBHHHBB', rcv_packet[0:10])
		[self.ip_check] = unpack('H', rcv_packet[10:12])
		[src_addr, dest_addr] = unpack('!4s4s', rcv_packet[12:20])
		
		self.ip_ihl = self.ip_ihl_ver & 0x0f
		self.ip_ver = (self.ip_ihl_ver & 0xf0) >> 4
		self.ip_flag_df = (self.ip_flag_frag & 0x40) >> 14
		self.ip_flag_mf = (self.ip_flag_frag & 0x20) >> 13
		self.ip_frag_off = self.ip_flag_frag & 0x1f
		self.ip_saddr = socket.inet_ntoa(src_addr)
		self.ip_daddr = socket.inet_ntoa(dest_addr)

		#print "dest addr from server : %s" %(self.ip_daddr)
		self.data = rcv_packet[self.ip_ihl*4:self.ip_total_len]
		pesudo_ip_header = rcv_packet[:self.ip_ihl*4]
		
		#print "IP checksum :%s" %(self.ip_checksum(pesudo_ip_header))
		if self.ip_checksum(pesudo_ip_header) != 0:
		    raise ChecksumError('IP')

class IPSocket:
	def __init__(self, saddr='', daddr=''):
		#self.sock = DataLinkSocket()
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
			#self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
			#self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error , msg:
			sys.exit()
		try:
			self.sock_recv = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
		except socket.error , msg:
			print 'Socket could not be created RECV. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()
		self.src_addr = saddr 
		self.dest_addr = daddr

	def close(self):
		self.sock.close()	

	def send(self, data):
		#print "src_addr %s dest_addr %s" %(self.src_addr, self.dest_addr)
		outgoing_packet = IPPacket(self.src_addr, self.dest_addr, data)
		packet = outgoing_packet.build()
		try:
			#print "try sending packet ip"
			self.sock.sendto(packet, (self.dest_addr, 0))
		except socket.error, msg:
			print 'Socket error IP : ' +str(msg[0]) + ' Message : ' +msg[1]
			sys.exit()

	def recv(self):
		while True:
			incoming_packet = IPPacket()
			rcv_packet = self.sock_recv.recv(10000)
			try:
				incoming_packet.unbuild(rcv_packet)
			except (ChecksumError) as err:
				print err

			if incoming_packet.ip_proto == socket.IPPROTO_TCP and incoming_packet.ip_saddr == self.dest_addr and incoming_packet.ip_daddr == self.src_addr:
				return incoming_packet.data
