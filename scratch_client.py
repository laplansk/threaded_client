#!/usr/bin/env python

import socket
import Queue
import struct
from threading import Thread
from time import sleep

# server connection variables - these should not change
IP = "127.0.0.1"
PORT = 3030

# assemble the header bytes:
# 1. input header values
# 2. reduce values to single bytes
headerArray = {196, 96, 1, 0, 123}
headerBytes = bytearray(headerArray)

# get data to send from keyboard
dataToSend = raw_input("What would you like to send? ")

# append data to header
headerAndData = headerBytes + dataToSend

# establish connection with server
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(headerAndData, (IP, PORT))