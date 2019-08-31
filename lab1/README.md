*****README for EE542 Lab 1 Fall 2019*****
*******Sufyan Shaikh & Charlie Andre******
This lab was split into 5 parts.
I.		Linux Installation
II. 	Single Connection Server and Client
III.	Multiple Connection Server and Client
IV.		UDP Server and Client
V. 		Unix Server and Client

The code for this lab was written in C.
Please refer to the code zipped with this README.

This lab requires two computers on the Linux system and one router.

I. Linux Installation
	Simple enough, follow a youtube video or an online guide. Remember to back up your stuff just in case.

II. Single Connection Server and Client
	Compile the two codes, server.c and client.c to obtain to executables. // gcc server.c -o server 
	Designate one machine as server and one as client.
	Obtain IP of server to use for client. 
	Run the command, ./server [port no.], for example "./server 5000" On the client side, run the command ./client [IP of server] [Port No.], for example "./client 192.168.1.150 5000"

III. Multiple Connection Server and Client
	Please read the code and understand the additions made. Run the commands as before and you will notice the server does not exit after a connection.
	Compile the new server code, server_multiple_connections.c. 
	Client code remains the same.
	Run the commands as before and notice that the server does not exit after one connection.

IV. UDP Server and Client
	In this code we use a different protocol, compare with the other server codes and note the differences.
	Client code is also changed, please go over the changes and understand them. 

V. Unix Server and Client
	Code given to us. Only difference in Unix domain to Internet domain is form of address. Notice we include the 
	unix header, un.h. 