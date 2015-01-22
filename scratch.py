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
    def __init__(self, client):
        super(InputListener, self).__init__()

    #This method gets run upon calling the
    def run(self):
	sequenceNo = 1
        while True:
            dataToSend = raw_input("What would you like to send? ")
	    header = struct.pack('>H2B2I', MAGIC, 1, DATA, sequenceNo, SESSION_ID)
	    packet = header + dataToSend
	    client.sendto(packet, (IP, PORT))
	    client.settimeout(5)
	    sequenceNo += 1

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
    while True:
        try:
            rawResponse = client.recv(1024)
            response = struct.unpack('>H2B2I', message[:12])
	    # check that magic number and version are correct
	    if response[0] != 50273 or response[1] != 1:
		continue
	    if response
        except socket.timeout, e:
            if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                continue;
            elif e.args[0] == 'timed out':
                sendGoodbye()
            elif response == "HELLO":
                # TODO fire up listener and start listening for responses
                client.settimeout(None)
                inputListener = InputListener()
                inputListener.start()
                listen()
            else:
                print "error"
                sys.exit(1)

def sendGoodbye():
    # create and send goodbye header
    goodbyeMessage = struct.pack('>H2B2I', MAGIC, 1, GOODBYE, SequenceNo, SESSION_ID)
    client.sendto(goodbyeMessage, (IP, PORT))

    # wait 5 seconds for a GOODBYE response before exiting
    client.settimeout(5)
# TODO THIS GOODBYE CODE IS WRONG response == GOODBYE is just a plug
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
        inputListener = InputListener(client)
        inputListener.start()
        responseListen()

    except socket.timeout, e:
        if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
            continue
        elif e.args[0] == 'timed out':
            sendGoodbye()
