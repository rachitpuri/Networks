import socket
import sys
import ssl

class SimpleClient:

    def __init__(self, disconnectConnection):
        self.disconnectConnection = disconnectConnection

    # This functions opens the socket connection to server
    def connectToServer(self):
        # Create a TCP/IP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.arg_list = sys.argv
        host = self.arg_list[-2]
        port = 27993
        self.wrappedSocket = None
        if len(sys.argv) > 3:
            if '-s' in sys.argv:
                self.wrappedSocket = ssl.wrap_socket(self.client_socket, cert_reqs=ssl.CERT_NONE)
                port = 27994
            if '-p' in sys.argv:
                index = sys.argv.index('-p')
                port = int(sys.argv[index + 1])
        	
        # Connect the socket to the port where the server is listening
        server_address = (host, port)
        try:
            if self.wrappedSocket != None:
                self.wrappedSocket.connect(server_address);
            else:
                self.client_socket.connect(server_address)
        except socket.error:
            print ('Connection failed')
            sys.exit()

    # This function sends the HELLO message to server
    def sendHelloMessage(self):
        neu_id = self.arg_list[-1]
        message = 'cs5700fall2015 HELLO ' + neu_id + '\n'
        try:
            if self.wrappedSocket != None:
                self.wrappedSocket.write(bytes(message))
            else:	
                self.client_socket.send(bytes(message))
        except socket.error:
            print ('HELLO message not sent')
            sys.exit()

    # This function receives message from the server
    def receiveMessage(self):
        try:
            if self.wrappedSocket != None:
                self.receivedMessage = self.wrappedSocket.read()
            else:
                self.receivedMessage = self.client_socket.recv(1024)
        except socket.error:
            print ('Message not received from server')
            sys.exit()

        self.receivedMessage = self.receivedMessage.decode('UTF-8')            
        
        # check for BYE message 
        if 'BYE' in self.receivedMessage:
            self.disconnectConnection = True
        else:
            self.splitReceivedMessage = self.receivedMessage.split(' ')
            first_number = int(self.splitReceivedMessage[2])
            second_number = int(self.splitReceivedMessage[4])
            expression = self.splitReceivedMessage[3]

            if expression == "+":
                self.solution = first_number + second_number
            elif expression == "-":
                self.solution = first_number - second_number    
            elif expression == "*":   
                self.solution = first_number * second_number
            else:
                self.solution = int(first_number / second_number)

    # This function sends solution to server
    def sendSolution(self):

        solutionMessage = 'cs5700fall2015 ' + str(self.solution) + '\n'
        if self.wrappedSocket != None:
            self.wrappedSocket.write(bytes(solutionMessage))
        else:
            self.client_socket.send(bytes(solutionMessage))

    # This function is called when client receives BYE message from server
    def byeMessage(self):

        if 'Unknown_Husky_ID' in self.receivedMessage:
            print ('Incorrect NEUID. Please try again')
        else:
            splitByeMessage = self.receivedMessage.split(' ')
            secretFlag = splitByeMessage[2]
            print (secretFlag)
        if self.wrappedSocket != None:
            self.wrappedSocket.close()
        else:
            self.client_socket.close()

def main():
    client = SimpleClient(False)
    client.connectToServer()
    client.sendHelloMessage()

    while client.disconnectConnection == False:
        client.receiveMessage()
        if client.disconnectConnection == False:
            client.sendSolution()

    client.byeMessage()

if __name__ == "__main__":main()
