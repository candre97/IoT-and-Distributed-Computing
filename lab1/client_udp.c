#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

void error(const char *msg)
{
    perror(msg);
    exit(0);
}

int main(int argc, char *argv[])
{
    unsigned int length;
    int sockfd, portno, n;
    struct sockaddr_in serv_addr, cli_addr;
    struct hostent *server;

    char buffer[256];
    if (argc < 3) {
       fprintf(stderr,"usage %s hostname port\n", argv[0]);
       exit(0);
    }
    portno = atoi(argv[2]);
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) 
        error("ERROR opening socket");
    serv_addr.sin_family = AF_INET;
    server = gethostbyname(argv[1]);
    if (server == NULL) {
        fprintf(stderr,"ERROR, no such host\n");
        exit(0);
    }

    bcopy((char *)server->h_addr, 
         (char *)&serv_addr.sin_addr,
         server->h_length);
    serv_addr.sin_port = htons(portno);

    length = sizeof(struct sockaddr_in);
    printf("Please enter the message: ");
    bzero(buffer,256);
    fgets(buffer,255,stdin);
    n=sendto(sockfd,buffer, strlen(buffer),0,(const struct sockaddr *)&serv_addr,length);
    if (n < 0) 
        error("Sendto fail");
    n = recvfrom(sockfd,buffer,256,0,(struct sockaddr *)&cli_addr, &length);
    if (n < 0) 
         error("recvfrom fail");
    write(1, "ack received: ", 15);
    write(1, buffer, n);
    close(sockfd);
    return 0;
}