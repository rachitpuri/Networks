import socket
import sys
from struct import*
from random import randint
from ip import IPSocket
import re
import time
import commands
import collections

TIMEOUT = 180

class TimeoutException(Exception):
	"""docstring for TimeoutException"""
	def __init__(self):
		self.time = TIMEOUT
		
	def __str__(self):
		return "Timeout, waited for %s" %(self.time)

class ChecksumError(Exception):
	"""docstring for ChecksumError"""
	def __init__(self, layer=''):
		self.layer = layer
		
	def __str__(self):
		return "Checksum not correct at %s" %(self.layer)

class TCPSegment:
	def __init__ (self, src_port='', dst_port='', src_ip='', dst_ip='', data=''):
		self.src_port = src_port
		self.dest_port = dst_port
		self.seq_num = 0
		self.ack_num = 0
		self.data_off = 5
		self.syn = 0
		self.fin = 0
		self.ack = 0
		self.urg = 0
		self.psh = 0
		self.rst = 0
		self.wnd = 4096
		self.check = 0
		self.urg_ptr = 0
		self.src_ip = src_ip
		self.dest_ip = dst_ip
		self.data = data 

	def carry_around_add(self, s):
		c = (s >> 16) + (s & 0xffff)
		c += c >> 16
		c = ~c& 0xffff
		return c

	def tcp_checksum(self, msg): 
		if len(msg) % 2 != 0:
		    msg = msg + pack('B', 0)
		s = 0
		for i in range(0, len(msg), 2):
			w = ord(msg[i]) + (ord(msg[i+1]) << 8)
			s += w
		s = self.carry_around_add(s)
		return s

	def build(self):
		src_ip = socket.inet_aton(self.src_ip)
		dest_ip = socket.inet_aton(self.dest_ip)
		
		offset_res = (self.data_off << 4) + 0
		tcp_flags = self.fin + (self.syn << 1) + (self.rst << 2) + (self.psh << 3) + (self.ack << 4) + (self.urg << 5)

		tcp_header = pack('!HHLLBBHHH', self.src_port, self.dest_port, self.seq_num, self.ack_num, offset_res, tcp_flags, 
						   self.wnd, self.check, self.urg_ptr)
		padding = 0
		self.check = 0
		psuedo_tcp_header = pack('!4s4sBBH', src_ip, dest_ip, padding, socket.IPPROTO_TCP, self.data_off * 4 + len(self.data))
		segment = psuedo_tcp_header + tcp_header + self.data
		self.check = self.tcp_checksum(segment)
		#print (self.check)
	
		tcp_header_new = pack('!HHLLBBH', self.src_port, self.dest_port, self.seq_num, self.ack_num, offset_res, tcp_flags, 
							   self.wnd) + pack('H', self.check) + pack('!H', self.urg_ptr)
		tcp_segment = tcp_header_new + self.data
		return tcp_segment

	def unbuild(self,rcv_segment):
		[self.src_port, self.dest_port, self.seq_num, self.ack_num, offset, flags, \
		self.wnd] = unpack('!HHLLBBH', rcv_segment[0:16])
		[self.check] = unpack('H', rcv_segment[16:18])
		[self.urg_ptr] = unpack('!H', rcv_segment[18:20])
		header_len = offset >> 4

		self.fin = flags & 0x01
		self.syn = (flags & 0x02) >> 1
		self.rst = (flags & 0x04) >> 2
		self.psh = (flags & 0x08) >> 3
		self.ack = (flags & 0x10) >> 4
		self.urg = (flags & 0x20) >> 5
		
		self.data = rcv_segment[header_len * 4:]
		src_ip = socket.inet_aton(self.src_ip)
		dest_ip = socket.inet_aton(self.dest_ip)
		padding = 0

		tcp_length = header_len*4 + len(self.data)
		psuedo_header = pack('!4s4sBBH', src_ip, dest_ip, padding, socket.IPPROTO_TCP, tcp_length)
		
		segment = psuedo_header + rcv_segment
		#print "tcp checksum %s " %(self.tcp_checksum(segment))
		#if self.tcp_checksum(segment) != 0:
		#	raise ChecksumError('TCP')

class TCPSocket:
	def __init__(self):
		self.src_ip = ''
		self.dest_ip = ''
		self.src_port = 0
		self.dst_port = 0
		self.seq_num = 0
		self.ack_num = 0
		self.sock = IPSocket()
		self.ack_count = 0
		self.cwnd = 1 
		self.MSS = 536
	
	""" Get public IP of your machine and not localhost
	"""
	def get_src_ip(self):
		ip_config = commands.getoutput("/sbin/ifconfig") 
		ip_address_candidate = re.findall("inet addr:(.*?) ", ip_config)
		for ip in ip_address_candidate:
			if ip != '127.0.0.1':
				return ip	

	""" Create a socket bind it with ethernet to get some port
		and then close the connection 
	"""
	def get_free_port(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', 0))
		port = s.getsockname()[1]
		s.close()
		return port

	""" Creates a SYN/ACK packet  
	"""
	def send_syn_ack_packet(self, syn, ack):
		packet = TCPSegment(self.src_port, self.dst_port, self.src_ip, self.dst_ip)
		packet.syn = syn
		packet.ack = ack
		packet.seq_num = self.seq_num
		packet.ack_num = self.ack_num
		return packet

	def build_send_packet(self, data=''):
		packet = TCPSegment(self.src_port, self.dst_port, self.src_ip, self.dst_ip, data)
		packet.seq_num = self.seq_num
		packet.ack_num = self.ack_num
		return packet

	def recv(self):
		#print "hello recv "
		tcp_data = ''
		packet = TCPSegment()
		
		def parse_header(response):
			index = response.find('\r\n\r\n') + 4
			header = response[:index]
			return header[9:12], index

		while True:
			if self.ack_count >= 1:
				# Send ACK packet
				packet = self.build_send_packet('')
				packet.ack_num = self.ack_num
				packet.seq_num = self.seq_num
				packet.ack = 1
				self.sock.send(packet.build())
				self.ack_count -= 1

			try:
				packet = self.receive_packet()
			except (TimeoutException, ChecksumError) as err:
				raise err
			
			#print "packet seq , packet_ack, self_req_num, self_ack_num (%s, %s, %s, %s) " %(packet.seq_num, packet.ack_num, self.seq_num, self.ack_num)
			if packet.seq_num == self.ack_num:
				data = packet.data
				#print (data)
				pos = 0
				if data.startswith('HTTP/1.1'):
					status, pos = parse_header(data)
					if status != '200':
						sys.exit('The HTTP Response has an  abnormal status code.')
					else:
						pass
				tcp_data += data[pos:]
			else:
				pass

			self.ack_num = packet.seq_num + len(packet.data)
			self.seq_num = packet.ack_num
			if self.cwnd > 1000:
				self.cwnd = 1000
			else: 
				self.cwnd + 1
			
			# Increase ack_count by 1
			self.ack_count += 1
			
			if packet.fin == 1:
				packet = self.build_send_packet('')
				# Set ACK for previous packet
				packet.ack_num = self.ack_num
				packet.seq_num = self.seq_num
				packet.ack = 1
				packet.fin = 1
				self.sock.send(packet.build())
				break
		return tcp_data

	def receive_packet(self):
		packet = TCPSegment()
		start_time = time.time()
		while (time.time() - start_time) < TIMEOUT:
			try:
				response = self.sock.recv()
			except:
				continue
			
			packet.src_ip = self.dst_ip
			packet.dest_ip = self.src_ip
			packet.unbuild(response)
			
			if packet.src_port == self.dst_port and packet.dest_port == self.src_port:
				#print "return TCP packet with data %s" %(packet.ack_num)
				return packet
			else:
				pass
			 	#print "src and dest port does not match"
		else:
			raise TimeoutException

	def connect(self, hostname, port):
		self.src_port = self.get_free_port()
		self.dst_port = port
		
		self.src_ip = self.get_src_ip()
		self.dst_ip = socket.gethostbyname(hostname)
		
		# Update the IPSocket
		self.sock = IPSocket(self.src_ip, self.dst_ip)

		# Get random Sequence number to send first packet
		self.seq_num = randint(0, 65535)

		# Send SYN packet to establish connection with server
		packet = self.send_syn_ack_packet(1, 0)
		self.sock.send(packet.build())
		
		# receive SYN+ACK from server for the sent SYN packet
		try:
			packet = self.receive_packet()
		except (TimeoutException, ChecksumError) as err:
			print err

		#print "connect packet seq, packet.ack_num, self_seq send time, self.ack_num: (%s, %s, %s, %s)" %(packet.seq_num, packet.ack_num, self.seq_num, self.ack_num)
		if packet.ack_num == (self.seq_num + 1) and packet.syn == 1 and packet.ack == 1:
			self.ack_num = packet.seq_num + 1
			self.seq_num = packet.ack_num
			if self.cwnd > 1000:
				self.cwnd = 1000
			else:
				self.cwnd += 1
		else:
			print 'wrong SYN+ACK Packet'
		   
		# Send ACK
		packet = self.send_syn_ack_packet(0, 1)
		self.sock.send(packet.build())
		print 'Handhsake Successful'

	def send(self,request):
		print "Sending GET request "
		#print "self.seq_num and self.ack_num(%s, %s)" %(self.seq_num, self.ack_num)
		print (request)
		packet = self.build_send_packet(request)
		packet.ack = 1
		packet.psh = 1
		self.sock.send(packet.build())

		try:
			packet = self.receive_packet()
			#print "data received %s" %(packet)
		except:
			raise TimeoutException

		#print "Before packet seq, packet.ack_num, self_seq send time, self.ack_num: (%s, %s, %s, %s)" %(packet.seq_num, packet.ack_num, self.seq_num, self.ack_num)
		if packet.ack_num == (self.seq_num + len(request)):
			self.ack_num = packet.seq_num + len(packet.data)
			self.seq_num = packet.ack_num
			if self.cwnd > 1000:
				self.cwnd = 1000
			else:
				self.cwnd += 1

		else:
			print 'wrong SYN+ACK Packet'

	def close(self):
		# Send FIN+ACK
		packet = self.build_send_packet()
		packet.fin = 1
		self.sock.send(packet.build())

		try:
			packet = self.receive_packet()
		except (TimeoutException, ChecksumError) as err:
			raise err
		
		if packet.ack_num == (self.seq_num + 1) and packet.fin == 1 and packet.ack == 1:
			print "Connection Closed"
			self.ack_num = packet.seq_num + 1
			self.seq_num = packet.ack_num
		
		# send ack
		packet = self.build_send_packet()
		packet.ack = 1
		self.sock.send(packet.build())
		self.sock.close()