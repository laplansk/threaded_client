#!/usr/bin/env python

import socket
import sys
from threading import Thread
import random
import struct

# global flag; TRUE indicates that all threads should terminate
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

        # loop to get user input
        while True:
            try:
                dataToSend = raw_input()
                if dataToSend == 'q':
                    client.settimeout(None)
                    END = True
                    sendGoodbye()
                    sys.exit()
                else:
                    header = struct.pack('>H2B2I', MAGIC, VERSION, DATA, SequenceNo, SESSION_ID)
                    SequenceNo += 1
                    packet = header + dataToSend
                    client.sendto(packet, (IP, PORT))
                    client.settimeout(5)
            except socket.timeout:
                END = True
                sendGoodbye()
                break
            except EOFError:
                print "eof1"
                END = True
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
            rawResponse = client.recv(2048)
            response = struct.unpack('>H2B2I', rawResponse[:12])
            if response[2] == GOODBYE:
                END = True
                sys.exit(0)
        except socket.timeout:
            END = True
            sys.exit(0)


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

        # server connection variables
        global IP
        global PORT
        global MAGIC
        global VERSION
        global SequenceNo
        global SESSION_ID
        global client
        
        # assemble the header bytes for HELLO / initial message:
        helloMessage = struct.pack('>H2B2I', MAGIC, 1, HELLO, SequenceNo, SESSION_ID)
        client.sendto(helloMessage, (IP, PORT))
        client.settimeout(5)

        # expect response within timeout
        while True:
            try:
                message = client.recv(1024)
                response = struct.unpack('>H2B2I', message[:12])
                if response[0] != 50273 or response[1] != 1:
                    continue
                elif response[2] == HELLO:
                    client.settimeout(None)
                    SequenceNo += 1
                    # fire up listener and start listening for responses from server
                    inputListener = InputListener(client)
                    inputListener.setDaemon(True)
                    inputListener.start()
                    # loop, listening for responses from server
                    while not END:
                        try:
                            rawResponse = client.recv(1024)
                            response = struct.unpack('>H2B2I', rawResponse[:12])  # check that magic number and version are correct
                            if response[0] != 50273 or response[1] != 1:
                                continue
                            elif response[2] == ALIVE:
                                client.settimeout(None)
                            elif response[2] == GOODBYE:
                                END = True
                                client.settimeout(None)
                                sys.exit(0)
                        except socket.timeout as e:
                            if e.message == "time out":
                                sendGoodbye()
                                break
                        except EOFError:
                            print "eof2"
                            END = True
                            sys.exit()
                elif response[2] == GOODBYE:
                    END = True
                    sys.exit(0)
            except socket.timeout as e:
                if e.message == "time out":
                    sendGoodbye()
                    break


# get host and port from command line, create socket
IP = sys.argv[1];
PORT = int(sys.argv[2]);
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# start thread that will receive response from server
serverThread = ServerComm()
serverThread.setDaemon(True)
serverThread.start()

# loop until one of the threads signals otherwise by changing the global END
while not END:
    continue

sys.exit(0)

