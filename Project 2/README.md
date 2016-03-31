Run

<p>./webcrawler [username] [password]</p>
------------------------------------------------------------------------------------------------------

Strategy

1. Check the number of arguments passed. If they are missing then display a message stating arguments missing.
2. Send HTTP GET request to fakebook and get cookie
3. Send HTTP POST request to fakebook with username, password and cookied found above to login.
4. Use BFS to crawl webpages:<br>
   4.1 Get the first url and put it into a queue called urls (contains unvisited urls)<br>
   4.2 Pop a url from unvisited list and Send HTTP GET request to it. After visiting this url put this into the visited list called visited (containes url that have been visited)<br>
   4.3 Use regular expression to find urls links present in the visited url. Add all the links to queue which are not in the visited list.<br>
   4.4 Search for secret flag and if found add it to the flag list (contains all the secret flags)<br>
   4.5 Keep performing the BFS until all the urls have been visited or 5 secret flags have been found.<br>
5. Error Handling:<br>
   5.1 if status code is 301, parse the response message, get the redirect url and insert it into the urls queue<br>
   5.2 if status code is 403 or 404, abandon this url and put it into the visited list<br>
   5.3 if status code is 500, it's a server issue and client will try to re-connect and send the request again.<br>
  
---------------------------------------------------------------------------------------------------------

Challenges

1. The biggest challenge was understanding the protocol and how the GET and POST packets are formed.
2. Other challenge was handling the exceptions like: 301 for redirect
3. Avoiding loops A->B->A
4. Used chrome to understand the headers of request and used advanced REST client for testing
