#!/usr/bin/env python

import struct
MAGIC = struct.pack('H', 50237)
print '%(num)16d' % \
      {"num": MAGIC}


# print '%(language)s has %(number)03d quote types.' % \
#       {"language": "Python", "number": 2}