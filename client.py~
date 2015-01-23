#!/usr/bin/env python

import socket
import errno
import sys
from threading import Thread
from time import sleep
import random
import struct

END = False
# valid packet commands
HELLO = 0
DATA = 1
ALIVE = 2
GOODBYE = 3

# server connection variables - these should not change
IP = "127.0.0.1"
PORT = 0
MAGIC = 0xC461
VERSION = 1
SequenceNo = 0
SESSION_ID = random.getrandbits(32)


# Python's weird way of subclassing...
class InputListener(Thread):
    def __init__(self, client):
        super(InputListener, self).__init__()

    # This method gets run upon calling the 
    # start() method on an instance of this object
    def run(self):
        
        global END
        # valid packet commands
        global HELLO
        global DATA
        global ALIVE
        global GOODBYE

        # server connection variables - these should not change
        global IP
        global PORT
        global MAGIC
        global VERSION
        global SequenceNo
        global SESSION_ID
        global client

        while True:
            try:
                dataToSend = raw_input("What would you like to send? ")
                if dataToSend == 'q':
                    print "user typed q : sending goodbye message"
                    End = True
                    sendGoodbye()
                    sys.exit()
                else:
                    header = struct.pack('>H2B2I', MAGIC, VERSION, DATA, SequenceNo, SESSION_ID)
                    SequenceNo += 1
                    packet = header + dataToSend
                    client.sendto(packet, (IP, PORT))
                    client.settimeout(5)
            except socket.timeout:
                print "client timeout"
                sendGoodbye()
                break
            except EOFError:
                print "eof"
                END = True
                client.close()
                sys.exit()

def sendGoodbye():
    # create and send goodbye header
    goodbyeMessage = struct.pack('>H2B2I', MAGIC, 1, GOODBYE, SequenceNo, SESSION_ID)
    client.sendto(goodbyeMessage, (IP, PORT))
    global END
    # wait 5 seconds for a GOODBYE response before exiting
    client.settimeout(5)
    while True:
        try:
            rawResponse = client.recv(1024)
            response = struct.unpack('>H2B2I', rawResponse[:12])
            if response[2] == GOODBYE:
                print 'server reciprocated will to end connection'
                END = True
                client.close()
                sys.exit(0)
            else:
                print 'error'
                client.close()
                sys.exit(1)
        except socket.timeout:
            print 'timeout on goodbye'
            END = True
            client.close()
            sys.exit(0)





# Python's weird way of subclassing...
class ServerComm(Thread):
    def __init__(self):
        super(ServerComm, self).__init__()

    # This method gets run upon calling the 
    # start() method on an instance of this object
    def run(self):
        global END
        # valid packet commands
        global HELLO
        global DATA
        global ALIVE
        global GOODBYE

        # server connection variables - these should not change
        global IP
        global PORT
        global MAGIC
        global VERSION
        global SequenceNo
        global SESSION_ID
        global client
        
        # establish connection with server
        # if successful, launch listener
        # assemble the header bytes:
        helloMessage = struct.pack('>H2B2I', MAGIC, 1, HELLO, SequenceNo, SESSION_ID)
        client.sendto(helloMessage, (IP, PORT))
        client.settimeout(5)

        # check for response within timeout
        while True:
            try:
                message = client.recv(1024)
                response = struct.unpack('>H2B2I', message[:12])
                if response[0] != 50273 or response[1] != 1:
                    continue
                elif response[2] == HELLO:
                    # desired response received so cancel timer
                    client.settimeout(None)
                    SequenceNo += 1
                    # fire up listener and start listening for responses from server
                    inputListener = InputListener(client)
                    inputListener.setDaemon(True)
                    inputListener.start()
                    while not END:
                        try:
                            rawResponse = client.recv(1024)
                            response = struct.unpack('>H2B2I', rawResponse[:12])  # check that magic number and version are correct
                            if response[0] != 50273 or response[1] != 1:
                                print "continuing"
                                continue
                            elif response[2] == ALIVE:
                                client.settimeout(None)
                            elif response[2] == GOODBYE:
                                print "server sent goodbye message : disconnecting"
                                client.close()
                                sys.exit(0)
                        except socket.timeout:
                            print "client timeout"
                            sendGoodbye()
                            break
                        except EOFError:
                            print "eof"
                            END = True
                            client.close()
                            sys.exit()
                elif response[2] == GOODBYE:
                    print "server sent goodbye message : disconnecting"
                    END = True
                    client.close()	
                    sys.exit(0)
            except socket.timeout, e:
                print "timeout on HELLO"
                sendGoodbye()
                break


# get host and port from command line
IP = sys.argv[1];
PORT = int(sys.argv[2]);
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print "starting serverThread"
serverThread = ServerComm()
serverThread.setDaemon(True)
serverThread.start()
while not END:
    continue

print "exiting"
sys.exit(0)

