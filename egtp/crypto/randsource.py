#  Copyright (c) 2000 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.

__revision__ = "$Id: randsource.py,v 1.6 2003/02/10 17:26:16 zooko Exp $"

from egtp.crypto import evilcryptopp

__doc__ = evilcryptopp._randsource_doc
get = evilcryptopp._randsource_get

import time, sys, os, sha, string

if sys.platform == 'win32':
    # this is part of the win32all python package, get it from:
    # http://www.activestate.com/Products/ActivePython/win32all.html
    import win32api
    from egtp.crypto import win_entropy # A module that gets entropy on win32

# our modules

def add(seedbytes, entropybits):
    evilcryptopp._randsource_add(seedbytes, entropybits)
   

# TODO add entropy gathering for other OSes
if sys.platform == "win32":
    add(win_entropy.read(160), 160)
elif (string.find(sys.platform, "linux") != -1) or (string.find(string.lower(sys.platform), "darwin") != -1) or (string.find(string.lower(sys.platform), "bsd") != -1):
    urandomdata = open('/dev/urandom', 'rb').read(20)
    add(urandomdata, len(urandomdata)*8)
else:
    print 'WARNING: a better random entropy source is needed for this OS\n'
    add(sha.sha( sys.platform + sys.version + str(time.time()) ).digest(), 160)
