#  Copyright (c) 2003 Myers Carpenter
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.

__revision__ = "$Id: aesctr.py,v 1.2 2003/03/23 16:15:52 myers_carpenter Exp $"

from egtp.crypto import evilcryptopp

__doc__ = evilcryptopp._aesctr_doc
new = evilcryptopp._aesctr_new
Error = evilcryptopp.AESCTRError


def longtobytes(n,block=1): #Slow!
    r = ""
    while n>0:
        r = chr(n&0xff) + r
        n = n >> 8
    if len(r)% block:
        r = chr(0)*(block-len(r)%block) + r
    return r

