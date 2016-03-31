<b>Build</b>

<p>No need to build python files</p>
-------------------------------------------------------------------
<b>Run</b>

<p>./client <-p port> <-s> [hostname] [NEU ID]</p>
-------------------------------------------------------------------
<b>Strategy</b>

1. Parse arguments and connect with the server
2. Send HELLO message to server and receive a STATUS message with a mathematical expression.
3. Run a loop to solve expression until the client receives a BYE message. During each iteration, the client will compute the result     of given expression and send the solution back to server. If solution is correct then server will reply again with new expression. 
4. Parse the BYE message and extract secret_flag. (cs5700 fall2015 [a 64 byte secret flag] BYE\n)

<b>Challenges</b>

The main challenges we face is:
1. The biggest challenge was understanding the packet data and extracting correct information from it. If there is a slight error in solution being send to server, then server will disconnect the connection.
