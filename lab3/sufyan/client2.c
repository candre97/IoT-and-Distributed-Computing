#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <dirent.h>
#include <time.h>

#define BUFFER 16384	//Max buffer size of the data in a frame
#define NUM_OF_PACKETS 64000 //  File size / buffer size -> ex: 1GB/16KB = 64000
struct udp_frame {
	long int ID;
	long int length;
	char data[BUFFER];
};

static void print_error(char *msg)
{
	perror(msg);
	exit(EXIT_FAILURE);
}

int main(int argc, char **argv)
{
	if ((argc < 3) || (argc >3)) {
		printf("skeleton -> ./client [IP Address] [Port Number]\n"); 
		exit(EXIT_FAILURE);
	}

	struct sockaddr_in send_addr, from_addr;
	struct stat st;
	struct udp_frame frame;
	struct timeval t_out = {0, 0};

	char cmd_send[100];
	char filename[50];
	char cmd[20];
	char ack_send[4] = "ACK";

	int dropped_buffer[1000];
	int data_buffer[NUM_OF_PACKETS];
	int length_buffer[NUM_OF_PACKETS];
	
	ssize_t num_read = 0;
	ssize_t length = 0;
	off_t f_size = 0;
	long int ack_num = 0;
	int cfd, ack_recv = 0;

	int k = 0;

	FILE *fptr;

	/*Clear all the data buffer and structure*/
	memset(ack_send, 0, sizeof(ack_send));
	memset(&send_addr, 0, sizeof(send_addr));
	memset(&from_addr, 0, sizeof(from_addr));

	/*Populate send_addr structure with IP address and Port*/
	send_addr.sin_family = AF_INET;
	send_addr.sin_port = htons(atoi(argv[2]));
	send_addr.sin_addr.s_addr = inet_addr(argv[1]);

	if ((cfd = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
		print_error("Client: socket");

	for (;;) {
		memset(cmd_send, 0, sizeof(cmd_send));
		memset(cmd, 0, sizeof(cmd));
		memset(filename, 0, sizeof(filename));

		printf("\nTo retrieve file, please type command like\nget [file_name]\nTo exit please type 'exit' \n");
		printf("\n[user] ");
		scanf(" %[^\n]%*c", cmd_send);
		
		sscanf(cmd_send, "%s %s", cmd, filename);		//parse the user input into command and filename

		if (sendto(cfd, cmd_send, sizeof(cmd_send), 0, (struct sockaddr *) &send_addr, sizeof(send_addr)) == -1)
			print_error("Client: send");

		//GET
		if ((strcmp(cmd, "get") == 0) && (filename[0] != '\0' )) {
			long int total_frame = 0;
			long int bytes_rec = 0, i = 0;
			t_out.tv_sec = 2;
			setsockopt(cfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&t_out, sizeof(struct timeval)); 	//Enable timeout if client does not respond
			recvfrom(cfd, &(total_frame), sizeof(total_frame), 0, (struct sockaddr *) &from_addr, (socklen_t *) &length); //Get the # of frames to receive
			t_out.tv_sec = 0;
            setsockopt(cfd, SOL_SOCKET, SO_RCVTIMEO, (char *)&t_out, sizeof(struct timeval)); 	//Disable timeout
			

			if (total_frame > 0) {
				sendto(cfd, &(total_frame), sizeof(total_frame), 0, (struct sockaddr *) &send_addr, sizeof(send_addr));
				printf("# of frames: %ld\n", total_frame);	
				//fptr = fopen(filename, "wb");	//open the file in write mode

				//Receive acks and frames
				for (i = 1; i <= total_frame; i++)
				{
					memset(&frame, 0, sizeof(frame));
					recvfrom(cfd, &(frame), sizeof(frame), 0, (struct sockaddr *) &from_addr, (socklen_t *) &length);  //Recieve the frame

					//keep track of which PACKETS were lost to recall for them 
					if ((frame.ID < i) || (frame.ID > i)){
						dropped_buffer[k] = i ;
						k++; 
						i = frame.ID;                   
					}

					else {
						//fwrite(frame.data, 1, frame.length, fptr);   /*Write the recieved data to the file*/
						data_buffer[i] = *frame.data;
						length_buffer[i] = frame.length;
						bytes_rec += frame.length;
					}

					//if (i == total_frame) {
					//	printf("File received!\n");
					//}
				}
					//send dropped buffer to server to let them know which packets to send again
					// sendto(cfd, &(dropped_buffer), k, 0, (struct sockaddr *) &send_addr, sizeof(send_addr));
					// //for loop to receive the dropped packets
					// int j =0;
					// int dropped_buffer2[]
					// for(int i = 0; i < k; i++){
					// 	recvfrom(cfd, &(frame), sizeof(frame), 0, (struct sockaddr *) &from_addr, (socklen_t *) &length);  //Recieve the frame
					// 	if(dropped_buffer[i] = frame.ID){
					// 		//add dropped frames to the data buffers
					// 		data_buffer[frame.ID] = *frame.data;
					// 		length_buffer[frame.ID] = frame.length;
					// 	}
					// 	else {
					// 		dropped_buffer2[j] = dropped_buffer[i];
					// 		j++;
					// 	}
					}
			
				printf("%s", k);
				printf("Total bytes received = %ld\n", bytes_rec);
				//fclose(fptr);
			}
			else
				printf("Empty file!\n");
		}

		//EXIT
		else if (strcmp(cmd, "exit") == 0)
			exit(EXIT_SUCCESS);

		//INVALID CASE
		else
			printf("Invalid Command!\n");
	}		
	close(cfd);
	exit(EXIT_SUCCESS);
}
