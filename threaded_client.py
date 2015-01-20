# applicant = raw_input("Enter the applicant's name: ")
# interviewer = raw_input("Enter the interviewer's name: ")
# time = raw_input("Enter the appointment time: ")
# print interviewer + " will interview " + applicant + " at " + time

import socket
import time

numSends = 0
while True:
    dataToSend = raw_input('What would you like to send to the server on port 3030?')
    PORT = 3030
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host = socket.gethostname()
    host = ""
    client.connect((host, PORT))
    numSends += 1
    client.sendto(bytes(dataToSend), (host, PORT))
    client.shutdown(socket.SHUT_RDWR)
    client.close()
    time.sleep(1)

#########################################################