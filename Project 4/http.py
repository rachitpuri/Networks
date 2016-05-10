import sys
import socket
from tcp import TCPSocket

class HTTP:
	def __init__(self, url):
		self.sock = TCPSocket()
		self.hostname = url.split('/')[2]
		self.path = url[(url.find(self.hostname) + len(self.hostname)):]

	def download(self, url):
		filename = ""
		if url.endswith('/'):
			filename = 'index.html'
		else:
			filename = url.split('/')[-1]

		fp = open(filename, 'wb+')
		try:
			#print 'hostname : %s' %(self.hostname)
			self.sock.connect(self.hostname, 80)
		except socket.error:
			sys.exit('Connection Failed')

		try:
			request = "GET " + self.path + " HTTP/1.1\r\n" + "Host: " + self.hostname + "\r\n\r\n"
			# send HTTP request
			self.sock.send(request)
			# receive HTTP response
			data = self.sock.recv()
		except socket.error:
			sys.exit('Send Failed')
		else:
			fp.write(data)	
		finally:
			fp.close()

	def close(self):
		self.sock.close()

def main():
	if (len(sys.argv) != 2):
		sys.exit("Illegal Arguments")
	url = sys.argv[1]
	sock = HTTP(url)
	sock.download(url)
	sock.close()

if __name__ == "__main__":
	main()
