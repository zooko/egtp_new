#!/usr/bin/env python
#
#  Copyright (c) 2001 Autonomous Zone Industries
#  This file is licensed under the
#    GNU Lesser General Public License v2.1.
#    See the file COPYING or visit http://www.gnu.org/ for details.
#
# A module containing user-configuration utilities.
# (And it's pronounced confu-tils, where "confu" sounds like the beginning of "confusion".) 
#
# BirthDate: 2000-06-08
# CVS:
__cvsid = '$Id: confutils.py,v 1.3 2002/08/17 21:01:43 zooko Exp $'


# standard modules
import os.path
import sys
import types

# pyutil modules
from pyutil.config import DEBUG_MODE
from pyutil.debugprint import debugprint
from pyutil import humanreadable

true = 1
false = 0

from mojostd import confman, platform

## These functions are used to ensure that retrieved prices from confutils
## are always integers.  yeah, it's ugly
def _integerizePriceMap(tmap):
    for key in tmap.keys():
        tmap[key] = int(round(float(tmap[key])))
    return tmap

def integerizePrice(price):
    if(type(price) == types.DictType):
        return _integerizePriceMap(price)
    return int(round(float(price)))
