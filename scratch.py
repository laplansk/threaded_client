#!/usr/bin/env python

import struct


MAGIC_NUMBER = struct.pack('>H', 50237)
print MAGIC_NUMBER