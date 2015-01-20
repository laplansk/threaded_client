#!/usr/bin/env python

import socket
import Queue
import struct
from threading import Thread
from time import sleep


#Python's weird way of subclassing...
class InputListener(Thread):
    def __init__(self, clientArg):
        self.client = clientArg
        super(InputListener, self).__init__()

    #This method gets run upon calling the
    def run(self):
        while True:
            dataToSend = raw_input("What would you like to send? ")
            self.client.processInput(dataToSend)


# server connection variables - these should not change
IP = "10.0.1.31"
PORT = 3030

#constant header fields
MAGIC = struct.pack_into('H', 50237)


class Client():
    def __init__(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def processInput(self, dataToSend):
        self.client.sendto(dataToSend, (IP, PORT))

# immediately start listening for keyboard input
c = Client()
inputs = InputListener(c)
inputs.start();