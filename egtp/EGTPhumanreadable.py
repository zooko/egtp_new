#!/usr/bin/env python

#
#  Copyright (c) 2002 Bryce "Zooko" Wilcox-O'Hearn
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.
#
# CVS:
__cvsid = '$Id: EGTPhumanreadable.py,v 1.4 2002/09/09 21:15:13 myers_carpenter Exp $'

# standard modules
import string 

# pyutil modules
from pyutil import humanreadable
from egtp.mojosixbit import _asciihash_re, b2a

true = 1
false = 0

nulltrans = string.maketrans('', '')
printableascii = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=+!@#$%^&*()~[]\{}|;':\",./<>? \t" # I just typed this in by looking at my keyboard.  It probably doesn't matter much if I missed some, because I only use it to guess whether a 20-byte string should be represented as a string or as an ID.  If all of the characters in the string are found `printableascii', then we guess that it is a string, not an id.

class EGTPRepr(humanreadable.BetterRepr):
    """
    @subclasses BetterRepr: and represents 20-byte "unique ID" strings as "<abcde>" base-32 abbreviations.
    """
    def __init__(self):
        BetterRepr.__init__(self)
        self.repr_string = self.repr_str

    def repr_str(self, obj, level, asciihashmatch=_asciihash_re.match, b2a=b2a, translate=string.translate, nulltrans=nulltrans, printableascii=printableascii):
        if len(obj) == 20:
            # But maybe it was just a 20-character human-readable string, like "credit limit reached", so this is an attempt to detect that case.
            if len(translate(obj, nulltrans, printableascii)) == 0:
                if self.maxourstring >= 22:
                    return `obj`
