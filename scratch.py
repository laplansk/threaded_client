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
    def __init__(self, seqNo):
        super(InputListener, self).__init__()

    # This method gets run upon calling the
    def run(self):
        while True:
            try:
                dataToSend = raw_input("What would you like to send? ")
                # check if user wants to quit
                if dataToSend == 'q':
                    print "user typed q : sending goodbye message"
                    sendGoodbye()
                    break
                else:
                    header = struct.pack('>H2B2I', MAGIC, 1, DATA, SequenceNo, SESSION_ID)
                    SequenceNo += 1
                    packet = header + dataToSend
                    client.sendto(packet, (IP, PORT))
                    client.settimeout(5)
            except (EOFError):
                client.shutdown(socket.SHUT_RDWR)
                sys.exit()

# valid packet commands
HELLO = 0
DATA = 1
ALIVE = 2
GOODBYE = 3

# server connection variables - these should not change
IP = "127.0.0.1"
PORT = 3030
MAGIC = 0xC461
VERSION = 1
SequenceNo = 0
SESSION_ID = random.getrandbits(32)


def responseListen():
    while True:
        try:
            rawResponse = client.recv(1024)
            response = struct.unpack('>H2B2I', rawResponse[:12])  # check that magic number and version are correct
            if response[0] != 50273 or response[1] != 1:
                continue
            elif response[2] == ALIVE:
                client.settimeout(None)
            elif response[2] == GOODBYE:
                print "server send goodbye message : disconnecting"
                client.shutdown(socket.SHUT_RDWR)
                sys.exit(0)
        except socket.timeout, e:
            if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                continue
            elif e.args[0] == 'timed out':
                sendGoodbye()
                break
            else:
                print "error"
                client.shutdown(socket.SHUT_RDWR)
                sys.exit(1)


def sendGoodbye():
    # create and send goodbye header
    goodbyeMessage = struct.pack('>H2B2I', MAGIC, 1, GOODBYE, SequenceNo, SESSION_ID)
    client.sendto(goodbyeMessage, (IP, PORT))

    # wait 5 seconds for a GOODBYE response before exiting
    client.settimeout(5)
    while True:
        try:
            rawResponse = client.recv(1024)
            response = struct.unpack('>H2B2I', rawResponse[:12])
            if response[2] == 'GOODBYE':
                print 'server reciprocated will to end connection'
                client.shutdown(socket.SHUT_RDWR)
                sys.exit(0)
            else:
                print 'error'
                client.shutdown(socket.SHUT_RDWR)
                sys.exit(1)
        except socket.timeout, e:
            if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                continue
            elif e.args[0] == 'timed out':
                print 'timeout on goodbye'
                client.shutdown(socket.SHUT_RDWR)
                sys.exit(0)


# establish connection with server
# if successful, launch listener
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
            inputListener.start()
            responseListen()
        elif response[2] == GOODBYE:
            print "server sent goodbye message : disconnecting"
            client.shutdown(socket.SHUT_RDWR)
            sys.exit(0)

    except socket.timeout, e:
        if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
            continue
        elif e.args[0] == 'timed out':
            sendGoodbye()
            break
