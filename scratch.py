#!/usr/bin/env python

import socket
import errno
import sys
from threading import Thread
from time import sleep
import random
import struct

# Python's weird way of subclassing...
class InputListener(Thread):
    def __init__(self):
        super(InputListener, self).__init__()
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def processInput(self, packet):
        self.connection.sendto(packet, (IP, PORT))

    #This method gets run upon calling the
    def run(self):
        while True:
            dataToSend = raw_input("What would you like to send? ")
            self.client.processInput(dataToSend)

# valid packet commands
HELLO = 0
DATA = 1
ALIVE = 2
GOODBYE = 3

# server connection variables - these should not change
IP = "127.0.0.1"
PORT = 1200
MAGIC = 0xC461
VERSION = 1
SESSION_ID = random.getrandbits(32)
SequenceNo = 0

def responseListen():
    # TODO define listening behavior
    while True:
        try:
            response = client.recv(1024)
             # unpack the struct and
        except socket.timeout, e:
            if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                continue;
            elif e.args[0] == 'timed out':
                sendGoodbye()
            elif response == "HELLO":
                # TODO fire up listener and start listening for responses
                inputListener = InputListener()
                inputListener.start()
                listen()
            else:
                print "error"
                sys.exit(1)

def sendGoodbye():
    # TODO send GOODBYE MESSAGE AND WAIT FOR RESPONSE BEFORE EXITING
    # create goodbye header
    # headerArray = {MAGIC1, MAGIC2, VERSION, GOODBYE}
    # headerBytes = bytearray(headerArray)
    # goodbyeMessage = str(headerBytes) + str(SequenceNo) + str(SESSION_ID)
    goodbyeMessage = struct.pack('>H2B2I', MAGIC, 1, GOODBYE, SequenceNo, SESSION_ID)
    client.sendto(goodbyeMessage, (IP, PORT))

    # wait 5 seconds for a GOODBYE response before exiting
    client.settimeout(5)

    while True:
        try:
            response = client.recv(1024)
        except socket.timeout, e:
            if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                continue
            elif e.args[0] == 'timed out':
                print 'timeout on goodbye'
                sys.exit(0)
            elif response == 'GOODBYE':
                print 'server reciprocated will to end connection'
                sys.exit(0)
            else:
                print 'error'
                sys.exit(1)





# establish connection with server
# if successful, launch listener
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# assemble the header bytes:
helloMessage = struct.pack('>H2B2I', MAGIC, 1, HELLO, SequenceNo, SESSION_ID)
client.sendto(helloMessage, (IP, PORT))
client.settimeout(5)
SequenceNo += 1

# check for response within timeout
while True:
    try:
        message = client.recv(1024)
        response = struct.unpack('>H2B2I', message[:12])
        print response[0]
        print response[1]
        print response[2]
        print response[3]
        print response[4]
            # TODO fire up listener and start listening for responses
            inputListener = InputListener()
            inputListener.start()
            responseListen()

    except socket.timeout, e:
        if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
            continue
        elif e.args[0] == 'timed out':
            sendGoodbye()