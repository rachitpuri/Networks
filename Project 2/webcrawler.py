
import re
import socket
import string
import sys

class Crawler:

    def __init__(self, username, password):
        self.host = 'fring.ccs.neu.edu'  # host name
        self.port = 80     # port number
        self.urls = []  # store unvisited urls
        self.visited = []  # store visited urls
        self.secretflag = []     # store secret flags
        self.csrftoken = ''  # cookie's csrftoken
        self.sessionid = ''  # cookie's sessionid
        self.username = username  # username
        self.password = password  # password
        #self.f = open('result.txt', 'a')
	
    def handle_request(self, request):
        # Send request to the server and receive response.
        try:
            self.sock.sendall(request)
        except socket.error:
            sys.exit('Error while sending request')

        response = self.sock.recv(100000)
        return response

    def connectToServer(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = (self.host, self.port)
        try:
            self.sock.connect(server_address)
        except socket.error:
            print ('Connection failed')
            sys.exit()

    def login(self):
        #Login to the fakebook and get cookie.
        request = 'GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\nHost: %s\r\n\r\n' % self.host

        response = self.handle_request(request)
        #print (response)
        mylist = response.split("\n")
        req_dict = dict()
        for line in mylist:
            if line.startswith("Set-Cookie"):
                name, tid = line.split(":")[1].split(";")[0].strip().split("=")
                req_dict[name] = tid
                if name == "csrftoken":
                    self.csrftoken = req_dict["csrftoken"]
        
        # Post request to server, send username and password to login fakebook
        postdata = 'username='+self.username+'&password='+self.password+'&csrfmiddlewaretoken='+self.csrftoken+'&next='
        request = 'POST /accounts/login/ HTTP/1.1\r\nHost: %s\r\nConnection: keep-alive\r\nContent-Length: %d' \
                  '\r\nContent-Type: application/x-www-form-urlencoded\r\nCookie: csrftoken=%s; sessionid=%s' \
                  '\r\n\r\n%s' % (self.host, len(postdata), self.csrftoken, self.sessionid, postdata)
        response = self.handle_request(request)
        #print (response)
        mylist = response.split("\n")
        req_dict = dict()
        for line in mylist:
            if line.startswith("Set-Cookie"):
                name, tid = line.split(":")[1].split(";")[0].strip().split("=")
                req_dict[name] = tid
                if name == "sessionid":
                    self.sessionid = req_dict["sessionid"]
        self.urls.extend(['/fakebook/'])

    def get_page_status(self, page):
        # get HTTP status code
        index = string.find(page, ' ')
        return page[index + 1: index + 4]

    def visit_url(self, url):
        # Visit the given url and return the reponse        
        request = 'GET %s HTTP/1.1\r\nHost: %s\r\nConnection: keep-alive\r\nCookie: csrftoken=%s; ' \
                  'sessionid=%s\r\n\r\n' % (url, self.host, self.csrftoken, self.sessionid)
        page = self.handle_request(request)
        #self.f.write(page)
        self.visited.append(url)  # this url is visited
        status = self.get_page_status(page)
        if status == '403' or status == '404':
            self.visited.append(link)  # abandon the URL
        elif status == '301':  # redirect to a new url
            self.urls.insert(0, self.get_new_url(page))
        elif status == '500':  # Internal Server Error
            self.connectToServer()
            self.visited.pop()
            self.urls.insert(0, url)
        elif status == '':
            self.connectToServer()
            self.visited.pop()
            self.urls.insert(0, url)
        return page

    def find_url(self, page):
        # Use regular expression to find urls in html page
        pattern = re.compile(r'<a href=\"(/fakebook/[a-z0-9/]+)\">')
        links = pattern.findall(page)
        # Find a new url that have not been visited or found and then add it to urls list
        self.urls.extend(filter(lambda l: l not in self.urls and l not in self.visited, links))

    def find_secret_flag(self, page):
        # Use regular expression to find secret flag in html page
        result = [a.start() for a in list(re.finditer('FLAG:', page))]
        for index in result:
            self.secretflag.extend([page[index + 6 : index + 64]])

    def get_new_url(self, page):
        # Parse the HTTP response header and get new url     
        pattern = re.compile(r'Location=http://fring\.ccs\.neu\.edu(/fakebook/[a-z0-9/]+)')
        return pattern.findall(page)[0]

    def run(self):
        # Use breadth first search to crawl fakebook   

        # if there are unvisited urls or less than 5 flags, continue the loop
        while self.urls and len(self.secretflag) < 5:
            link = self.urls.pop(0)
            page = self.visit_url(link)
            self.find_url(page)
            self.find_secret_flag(page)

        for flag in self.secretflag:
            print flag
        self.sock.close()
        #self.f.close()

def main():
    if (len(sys.argv) != 3):
        sys.exit('Illeagal Arguments.')
    #c = Crawler("001724259", "RUFQYRSI")
    #c = Crawler("001715469", "7EL4DU8X")
    c = Crawler(sys.argv[1], sys.argv[2])
    c.connectToServer()
    c.login()
    c.run()
    
if __name__ == '__main__':
    main()
